"""Primary script to run to convert an entire session of data using the NWBConverter."""
from neuroconv.utils import load_dict_from_file, dict_deep_update

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingNWBConverter
from pathlib import Path

example_path = Path("D:/ExampleNWBConversion")
example_session_id = example_path.stem
nwbfile_path = example_path / f"{example_session_id}.nwb"

metadata_path = Path(__file__) / "cowley2022mapping_metadata.yaml"

source_data = dict(
    Recording=dict(),
    LFP=dict(),
    Sorting=dict(),
    Behavior=dict(),
)

converter = Cowley2022MappingNWBConverter(source_data=source_data)

metadata = converter.get_metadata()
metadata_from_yaml = load_dict_from_file(metadata_path)
metadata = dict_deep_update(metadata, metadata_from_yaml)

converter.run_conversion(metadata=metadata, nwbfile_path=nwbfile_path)
