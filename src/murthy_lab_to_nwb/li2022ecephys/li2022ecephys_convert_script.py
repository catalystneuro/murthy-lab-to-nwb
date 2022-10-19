from pathlib import Path
import datetime
from zoneinfo import ZoneInfo

from murthy_lab_to_nwb.li2022ecephys import Li2022EcephysNWBConverter
from neuroconv.utils import load_dict_from_file, dict_deep_update

data_dir_path = Path("/home/heberto/Murthy-data-share/")
output_path = Path("/home/heberto/conversion_nwb/nwb/")

stub_test = False
if stub_test:
    output_path = output_path.parent / "nwb_stub"


source_data = dict()

# Add Ecephys data
file_path = data_dir_path / "ephys_demo_0007-0008.h5"
nwbfile_path = output_path / f"{file_path.stem}.nwb"

source_data.update(dict(Ecephys=dict(file_path=str(file_path))))

converter = Li2022EcephysNWBConverter(source_data=source_data)

# Session start time (missing time, only including the date part)
metadata = converter.get_metadata()

tzinfo = ZoneInfo("US/Eastern")
date = datetime.datetime.today()  # TO-DO: Get this from author
metadata["NWBFile"]["session_start_time"] = date

# Update default metadata with the metadata from the editable yaml file in this directory
editable_metadata_path = Path(__file__).parent / "li2022ecephys.yaml"
editable_metadata = load_dict_from_file(editable_metadata_path)
metadata = dict_deep_update(metadata, editable_metadata)

# Add some more subject metadata

# Set conversion options and run conversion
conversion_options = dict(
    Ecephys=dict(stub_test=stub_test),
)

converter.run_conversion(
    nwbfile_path=nwbfile_path,
    metadata=metadata,
    conversion_options=conversion_options,
    overwrite=True,
)
