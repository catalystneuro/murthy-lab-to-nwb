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
output_path = Path("/home/heberto/conversion_nwb/nwb/")
if stub_test:
    output_path = output_path.parent / "nwb_stub"


# All of this are in `all_subjects` here we only have video for the following subject
subject = "fly5"
lobula_columnar_neuron_cell_line = "LC10a"
# lobula_columnar_neuron_cell_line = "LC17"

experiment = "courtship_behavior"
example_session_id = f"{experiment}_{lobula_columnar_neuron_cell_line}_{subject}"
nwbfile_path = output_path / f"{example_session_id}.nwb"


# Extract only the number as this is used in the file paths of the videos.
cell_string = lobula_columnar_neuron_cell_line[2:]
fly_number = subject[3:]
fly_number = fly_number.rjust(2, "0")  # Pad with 0s
video_string = f"{cell_string}{fly_number}"
video_file_paths = [path for path in video_dir_path.iterdir() if video_string in path.stem]
source_data = dict(
    Movie=dict(file_paths=video_file_paths),
    Audio=dict(
        subject=subject,
        lobula_columnar_neuron_cell_line=lobula_columnar_neuron_cell_line,
        data_dir_path=str(data_dir_path),
        ),
    Behavior=dict(
        subject=subject,
        lobula_columnar_neuron_cell_line=lobula_columnar_neuron_cell_line,
        data_dir_path=str(data_dir_path),
    ),
)

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

# Set conversion options and run conversion
conversion_options = dict(
    Movie=dict(external_mode=True, stub_test=stub_test),
    Audio=dict(),
    Behavior=dict(),
)
converter.run_conversion(
    nwbfile_path=nwbfile_path,
    metadata=metadata,
    conversion_options=conversion_options,
    overwrite=True,
)
