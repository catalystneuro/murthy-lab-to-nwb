"Gets all available subjects from the pickled data"

from pathlib import Path
import json
import yaml
import pickle

# General location of the data
data_dir_path = Path("/home/heberto/Murthy-data-share/one2one-mapping")
roi_responses_dir_path = data_dir_path / "processed_data" / "LC_responses_dFf" / "responses"

pickled_file_path_list = [path for path in roi_responses_dir_path.iterdir() if path.suffix == ".pkl"]


cell_type_to_fly_id = {}
for pickled_file_path in pickled_file_path_list:

    unpickleFile = open(pickled_file_path, "rb")
    pickled_data = pickle.load(unpickleFile, encoding="latin1")

    cell_type_to_fly_id[pickled_file_path.stem] = list({data["file_id"] for data in pickled_data})

location_of_the_file = Path(__file__).parent
file_path_to_save = location_of_the_file / "all_subjects.json"
with open(file_path_to_save, "w") as outfile:
    json.dump(cell_type_to_fly_id, outfile)

file_path_to_save = location_of_the_file / "all_subjects.yaml"
with open(file_path_to_save, "w+") as outfile:
    yaml.dump(cell_type_to_fly_id, outfile, allow_unicode=True)
