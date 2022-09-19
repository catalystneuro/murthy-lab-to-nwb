"""Primary script to run to convert an entire session of data using the NWBConverter."""
import datetime
from zoneinfo import ZoneInfo


from neuroconv.utils import load_dict_from_file, dict_deep_update

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingNWBConverter
from pathlib import Path

# Parameters
stub_test = True

# Data directories
all_subjects_info_path = Path(__file__).parent / "all_subjects_info.yaml"
all_subjects_info = load_dict_from_file(all_subjects_info_path)

data_dir_path = Path("/home/heberto/Murthy-data-share/one2one-mapping")
video_dir_path = data_dir_path / "raw_data" / "courtship_behavior" / "videos"
audio_dir_path = Path(data_dir_path) / "raw_data" / "courtship_behavior" / "audio"

joint_positions_data_dir = Path(data_dir_path) / "processed_data" / "joint_positions"

output_path = Path("/home/heberto/conversion_nwb/nwb/")
if stub_test:
    output_path = output_path.parent / "nwb_stub"


# All of this are in `all_subjects` here we only have video for the following subject
subject = "fly5"
lobula_columnar_neuron_cell_line = "LC10a"
# lobula_columnar_neuron_cell_line = "LC17"

# Some parsing for file_path location
cell_string = lobula_columnar_neuron_cell_line[2:]  # Only the number is used in the video file paths.
fly_number = subject[3:].rjust(2, "0")  # Pad with 0s

experiment = "courtship_behavior"
example_session_id = f"{experiment}_{lobula_columnar_neuron_cell_line}_{subject}"
nwbfile_path = output_path / f"{example_session_id}.nwb"

source_data = dict()

# Add movie interface (path stem example 161101_10a05.avi)
video_string = f"{cell_string}{fly_number}"
video_file_paths = [path for path in video_dir_path.iterdir() if video_string in path.stem]
source_data.update(Movie=dict(file_paths=video_file_paths))

# Add audio interface (path stem example 161101_10a05bin.mat)
audio_string = f"{cell_string}{fly_number}"
audio_path = next(path for path in audio_dir_path.iterdir() if audio_string in path.stem)
audio_file_path = audio_dir_path / audio_path
source_data.update(Audio=dict(file_path=str(audio_file_path)))

# Add Behavior interface
cell_line_dir_name = f"structs_{lobula_columnar_neuron_cell_line}"
file_name = f"S_{subject}.mat"
sound_and_joints_data_path = joint_positions_data_dir / cell_line_dir_name / file_name
source_data.update(Behavior=dict(file_path=str(sound_and_joints_data_path)))

# Build the converter
converter = Cowley2022MappingNWBConverter(source_data=source_data)

# Session start time (missing time, only the date part)
metadata = converter.get_metadata()

date_string = video_file_paths[0].stem.split("_")[0]
date_string = f"20{date_string}"
tzinfo = ZoneInfo("US/Eastern")

metadata["NWBFile"]["session_start_time"] = datetime.datetime(
    year=int(date_string[0:4]), month=int(date_string[4:6]), day=int(date_string[6:8]), tzinfo=tzinfo
)

# Update default metadata with the one in the editable yaml file in this directory
editable_metadata_path = Path(__file__).parent / "cowley2022mapping_metadata.yaml"
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
