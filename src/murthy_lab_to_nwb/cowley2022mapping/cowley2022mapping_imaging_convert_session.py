"""Primary script to run to convert an entire session of data using the NWBConverter."""
import datetime
from zoneinfo import ZoneInfo

from neuroconv.utils import load_dict_from_file, dict_deep_update

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingImagingNWBConverter
from pathlib import Path


def imaging_session_to_nwb(subject, cell_line, data_dir_path, output_dir_path, stub_test=False, verbose=False):
    if verbose:
        print("---------------------")
        print("conversion for:")
        print(f"{cell_line=} and {subject=}")

    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Data directories
    calcium_imaging_dir_path = data_dir_path / "raw_data" / "calcium_imaging"
    roi_responses_dir_path = data_dir_path / "processed_data" / "LC_responses_dFf" / "responses"
    imaging_stimuli_dir_path = data_dir_path / "processed_data" / "LC_responses_dFf" / "stimuli" / "images"

    experiment = "imaging"
    session_id = f"{experiment}_{cell_line}_{subject}"
    nwbfile_path = output_dir_path / f"{session_id}.nwb"

    source_data = dict()

    # Add Imaging data
    subject_tiff_files_dir_path = calcium_imaging_dir_path / f"{cell_line}" / f"{subject}"
    source_data.update(
        dict(Imaging=dict(subject_tiff_files_dir_path=str(subject_tiff_files_dir_path), sampling_frequency=50))
    )

    # Add behavior
    responses_file_path = roi_responses_dir_path / f"{cell_line}.pkl"
    source_data.update(dict(Behavior=dict(responses_file_path=str(responses_file_path), subject=subject)))

    # Add single-cell segmentation
    source_data.update(dict(Segmentation=dict(responses_file_path=str(responses_file_path), subject=subject)))

    # Add stimuli
    source_data.update(dict(Stimuli=dict(stimuli_folder_path=str(imaging_stimuli_dir_path))))

    # Gather them all in a converter
    converter = Cowley2022MappingImagingNWBConverter(source_data=source_data, verbose=verbose)

    # Session start time (missing time, only including the date part)
    metadata = converter.get_metadata()

    date_string = subject.split("_")[1]
    date_string = f"20{date_string}"
    tzinfo = ZoneInfo("US/Eastern")
    metadata["NWBFile"]["session_start_time"] = datetime.datetime(
        year=int(date_string[0:4]), month=int(date_string[4:6]), day=int(date_string[6:8]), tzinfo=tzinfo
    )

    # Update default metadata with the metadata from the editable yaml file in this directory
    editable_metadata_dir = Path(__file__).parent / "metadata"
    editable_metadata_path = editable_metadata_dir / "cowley2022mapping_imaging_metadata.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)

    # Add some more subject metadata
    metadata["Subject"]["subject_id"] = subject.split("_")[0]

    # Set conversion options and run conversion
    conversion_options = dict(
        Imaging=dict(stub_test=stub_test),
    )
    converter.run_conversion(
        nwbfile_path=nwbfile_path,
        metadata=metadata,
        conversion_options=conversion_options,
        overwrite=True,
    )


if __name__ == "__main__":
    # Parameters for conversion
    stub_test = False  # Converts a only a stub of the data for quick iteration and testing
    data_dir_path = Path("~/Murthy-data-share/one2one-mapping")  # Change to your system's path
    output_dir_path = Path("~/conversion_nwb/")  # nwb files are written to this folder / directory

    subject = "fly5_210803_201"
    cell_line = "LC11"  # lobula_columnar_neuron cell line

    imaging_session_to_nwb(
        subject=subject,
        cell_line=cell_line,
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        stub_test=stub_test,
    )
