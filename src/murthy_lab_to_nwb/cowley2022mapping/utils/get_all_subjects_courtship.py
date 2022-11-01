from pathlib import Path
import yaml
from natsort import natsorted

data_dir_path = Path("/home/heberto/Murthy-data-share/one2one-mapping")
video_dir_path = data_dir_path / "raw_data" / "courtship_behavior" / "videos"

cell_line_to_subjects_dict = dict()
all_cell_lines_dir_list = [dir_path for dir_path in video_dir_path.iterdir() if dir_path.is_dir()]
all_cell_lines_dir_list = natsorted(all_cell_lines_dir_list, key=lambda x: x.stem)

for cell_line_dir in all_cell_lines_dir_list:
    subject_paths_in_cell_line = (subject_path for subject_path in cell_line_dir.iterdir() if subject_path.is_file())
    subjects_in_cell_line = [path.stem.split("_")[0] for path in subject_paths_in_cell_line]
    cell_line_to_subjects_dict[cell_line_dir.stem] = natsorted(subjects_in_cell_line)

location_of_the_file = Path(__file__).parent.parent
file_path_to_save = location_of_the_file / "metadata" / "courtship_subjects.yaml"
with open(file_path_to_save, "w+") as outfile:
    yaml.dump(cell_line_to_subjects_dict, outfile, allow_unicode=True, sort_keys=False)
