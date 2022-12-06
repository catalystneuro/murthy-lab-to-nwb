from pathlib import Path

from neuroconv.utils import load_dict_from_file

from murthy_lab_to_nwb.cowley2022mapping import courtship_session_to_nwb

# Parameters for conversion
stub_test = True  # Converts a only a stub of the data for quick iteration and testing
verbose = True  # Displays verbose information per conversion

data_dir_path = Path("~/Murthy-data-share/one2one-mapping")  # Change to your system's path
output_dir_path = Path("~/conversion_nwb/")  # nwb files are written to this folder / directory

# This should be changed to point to a local copy of:
# https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/cowley2022mapping/metadata/imaging_subjects.yaml
all_subjects_file_path = Path(__file__).parent / "metadata" / "courtship_subjects.yaml"
all_courtship_subjects = load_dict_from_file(all_subjects_file_path)

for cell_line, subjects_in_cell_line in all_courtship_subjects.items():
    for subject in subjects_in_cell_line:
        courtship_session_to_nwb(
            subject=subject,
            cell_line=cell_line,
            data_dir_path=data_dir_path,
            output_dir_path=output_dir_path,
            stub_test=stub_test,
            verbose=verbose,
        )
