"""Primary script to run to convert an entire session of data using the NWBConverter."""
import datetime
from zoneinfo import ZoneInfo


from neuroconv.utils import load_dict_from_file, dict_deep_update

from murthy_lab_to_nwb.cowley2022mapping_imaging import Cowley2022MappingImagingNWBConverter
from pathlib import Path

# Parameters
stub_test = True

# Data directories
all_subjects_info_path = Path(__file__).parent / "all_subjects.yaml"
data_dir_path = Path("/home/heberto/Murthy-data-share/one2one-mapping")
tiff_dir_path = data_dir_path / "raw_data" / "calcium_imaging" / "example_tiffs"
roi_responses_dir_path = data_dir_path / "processed_data" / "LC_responses_dFf" / "responses"

output_path = Path("/home/heberto/conversion_nwb/nwb/")
if stub_test:
    output_path = output_path.parent / "nwb_stub"

all_subjects_info = load_dict_from_file(all_subjects_info_path)

# All of this are in `all_subjects` here we only have video for the following subject
subject = "210803_201"
lobula_columnar_neuron_cell_line = "LC11"
# lobula_columnar_neuron_cell_line = "LC17"

experiment = "imaging"
example_session_id = f"{experiment}_{lobula_columnar_neuron_cell_line}_{subject}"
nwbfile_path = output_path / f"{example_session_id}.nwb"
source_data = dict()

# Confirm with authors between sampling 30 (as for the stimuli) vs 50 (as in the paper)
#source_data.update(dict(Imaging=dict(subject=subject, tiff_dir_path=str(tiff_dir_path), sampling_frequency=50)))

responses_file_path = roi_responses_dir_path / f"{lobula_columnar_neuron_cell_line}.pkl"
source_data.update(dict(Behavior=dict(responses_file_path=str(responses_file_path), subject=subject)))

converter = Cowley2022MappingImagingNWBConverter(source_data=source_data)

# Session start time (missing time, only the date part)
metadata = converter.get_metadata()

date_string = subject.split("_")[0]
date_string = f"20{date_string}"
tzinfo = ZoneInfo("US/Eastern")

metadata["NWBFile"]["session_start_time"] = datetime.datetime(
    year=int(date_string[0:4]), month=int(date_string[4:6]), day=int(date_string[6:8]), tzinfo=tzinfo
)

# Update default metadata with the one in the editable yaml file in this directory
editable_metadata_path = Path(__file__).parent / "cowley2022mappingimaging_metadata.yaml"
editable_metadata = load_dict_from_file(editable_metadata_path)
metadata = dict_deep_update(metadata, editable_metadata)

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
