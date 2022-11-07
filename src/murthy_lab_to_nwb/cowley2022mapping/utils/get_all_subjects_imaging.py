from pathlib import Path
import yaml
from natsort import natsorted

data_dir_path = Path("/media/heberto/TOSHIBA EXT/Murthy-data-share/one2one-mapping")
calcium_imaging_dir_path = data_dir_path / "raw_data" / "calcium_imaging"

cell_line_to_subjects_dict = dict()
all_cell_lines_dir_list = [dir_path for dir_path in calcium_imaging_dir_path.iterdir() if dir_path.is_dir()]
all_cell_lines_dir_list = natsorted(all_cell_lines_dir_list, key=lambda x: x.stem)

for cell_line_dir in all_cell_lines_dir_list:
    subject_paths_in_cell_line = (subject_path for subject_path in cell_line_dir.iterdir() if subject_path.is_dir())
    subjects_in_cell_line = [path.stem for path in subject_paths_in_cell_line]
    cell_line_to_subjects_dict[cell_line_dir.stem] = natsorted(subjects_in_cell_line)

location_of_the_file = Path(__file__).parent.parent
file_path_to_save = location_of_the_file / "metadata" / "imaging_subjects.yaml"
with open(file_path_to_save, "w+") as outfile:
    yaml.dump(cell_line_to_subjects_dict, outfile, allow_unicode=True, sort_keys=False)
