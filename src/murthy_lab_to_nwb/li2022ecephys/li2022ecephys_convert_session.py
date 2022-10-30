from pathlib import Path
import datetime
from zoneinfo import ZoneInfo

from murthy_lab_to_nwb.li2022ecephys import Li2022EcephysNWBConverter
from neuroconv.utils import load_dict_from_file, dict_deep_update


def lily_session_to_nwb(file_path, output_path, stub_test=False):

    file_path = Path(file_path)
    assert file_path.exists(), f"file path {file_path} does not exists"
    output_path = Path(output_path)
    if stub_test:
        output_path = output_path / "nwb_stub"
    output_path.mkdir(parents=True, exist_ok=True)

    session_id = f"ecephys_{file_path.stem}"
    nwbfile_path = output_path / f"{session_id}.nwb"

    source_data = dict()

    # Add Ecephys data
    source_data.update(dict(Ecephys=dict(file_path=str(file_path))))

    converter = Li2022EcephysNWBConverter(source_data=source_data)

    # Session start time (missing time, only including the date part)
    metadata = converter.get_metadata()

    tzinfo = ZoneInfo("US/Eastern")
    year = 2020
    month = 1
    day = 1
    datetime.datetime(year=year, month=month, day=day, tzinfo=tzinfo)
    date = datetime.datetime.today()  # TO-DO: Get this from author
    metadata["NWBFile"]["session_start_time"] = date

    # Update default metadata with the metadata from the editable yaml file in this directory
    editable_metadata_path = Path(__file__).parent / "li2022ecephys.yaml"
    editable_metadata = load_dict_from_file(editable_metadata_path)
    metadata = dict_deep_update(metadata, editable_metadata)

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


if __name__ == "__main__":

    # Parameters for conversion
    stub_test = False
    data_dir_path = Path("/home/heberto/Murthy-data-share/")
    output_path = Path("/home/heberto/conversion_nwb/")
    file_path = data_dir_path / "ephys_demo_0007-0008.h5"

    lily_session_to_nwb(
        file_path=file_path,
        output_path=output_path,
        stub_test=stub_test,
    )
