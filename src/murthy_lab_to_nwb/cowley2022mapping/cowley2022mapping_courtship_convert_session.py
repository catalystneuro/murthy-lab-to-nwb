"""Primary script to run to convert an entire session of data using the NWBConverter."""
import datetime
from zoneinfo import ZoneInfo

from neuroconv.utils import load_dict_from_file, dict_deep_update

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingCourtshipNWBConverter
from pathlib import Path


def courtship_session_to_nwb(subject, cell_line, data_dir_path, output_dir_path, stub_test=False):

    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Data directories
    video_dir_path = data_dir_path / "raw_data" / "courtship_behavior" / "videos"
    audio_dir_path = Path(data_dir_path) / "raw_data" / "courtship_behavior" / "audio"
    joint_positions_data_dir = Path(data_dir_path) / "processed_data" / "joint_positions"

    experiment = "courtship_behavior"
    session_id = f"{experiment}_{cell_line}_{subject}"
    nwbfile_path = output_dir_path / f"{session_id}.nwb"

    source_data = dict()

    # Add movie interface (path stem example 161101_10a05.avi)
    video_file_path_dir = video_dir_path / cell_line
    video_file_paths = [path for path in video_file_path_dir.iterdir() if subject in path.stem]
    source_data.update(Movie=dict(file_paths=video_file_paths))

    # Add audio interface (path stem example 161101_10a05bin.mat)
    audio_file_path_dir = audio_dir_path / cell_line
    audio_file_path = next(path for path in audio_file_path_dir.iterdir() if subject in path.stem)
    source_data.update(Audio=dict(file_path=str(audio_file_path)))

    # Add Behavior interface
    file_name = f"S_{subject}.mat"
    sound_and_joints_data_path = joint_positions_data_dir / cell_line / file_name
    source_data.update(
        Behavior=dict(file_path=str(sound_and_joints_data_path), video_file_path=str(video_file_paths[0]))
    )

    # Build the converter
    converter = Cowley2022MappingCourtshipNWBConverter(source_data=source_data)

    # Session start time (missing time, only the date part)
    metadata = converter.get_metadata()

    # Video name is written in subject_date_time format
    date_string, time_string = video_file_paths[0].stem.split("_")[1:]

    date_string = f"20{date_string}"
    tzinfo = ZoneInfo("US/Eastern")

    metadata["NWBFile"]["session_start_time"] = datetime.datetime(
        year=int(date_string[0:4]),
        month=int(date_string[4:6]),
        day=int(date_string[6:8]),
        hour=int(time_string[:2]),
        minute=int(time_string[2:4]),
        tzinfo=tzinfo,
    )

    # Update default metadata with the one in the editable yaml file in this directory
    editable_metadata_dir = Path(__file__).parent / "metadata"
    editable_metadata_path = editable_metadata_dir / "cowley2022mapping_courtship_metadata.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)

    # Add some more metadata
    metadata["Subject"]["subject_id"] = subject

    # Set conversion options and run conversion
    conversion_options = dict(
        Movie=dict(external_mode=True, stub_test=stub_test),
        Audio=dict(stub_test=stub_test),
        Behavior=dict(),
    )
    converter.run_conversion(
        nwbfile_path=nwbfile_path,
        metadata=metadata,
        conversion_options=conversion_options,
        overwrite=True,
    )


if __name__ == "__main__":

    # Parameters for conversion
    stub_test = False
    data_dir_path = Path("/home/heberto/Murthy-data-share/one2one-mapping")
    output_dir_path = Path("/home/heberto/conversion_nwb/")
    subject = "fly1"
    cell_line = "LC4"  # lobula_columnar_neuron cell line

    courtship_session_to_nwb(
        subject=subject,
        cell_line=cell_line,
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        stub_test=stub_test,
    )
