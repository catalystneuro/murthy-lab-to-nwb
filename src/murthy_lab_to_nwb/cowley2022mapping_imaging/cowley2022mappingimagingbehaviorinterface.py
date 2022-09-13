"""Primary class defining conversion of experiment-specific behavior."""
from pathlib import Path
import pickle

from pynwb.file import NWBFile, ProcessingModule
from neuroconv.basedatainterface import BaseDataInterface


class Cowley2022MappingImagingBehaviorInterface(BaseDataInterface):
    """My behavior interface docstring"""

    def __init__(self, responses_file_path: str, subject: str):
        # Point to data

        self.responses_file_path = Path(responses_file_path)
        assert self.responses_file_path.is_file()
        self.subject = subject

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible

        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict):
        # All the custom code to write through PyNWB
        with open(self.responses_file_path, "rb") as f:
            pickled_data = pickle.load(f, encoding="latin1")

        subject_data = [data for data in pickled_data if data["file_id"] == self.subject]

        trial_dict_list = []

        for trial_data in subject_data:
            timestamps = trial_data["timepts"]
            stimulus = trial_data["stimulus"]
            stimulus_name = trial_data.get("stim_name", "")
            for trial_timestamps in timestamps:  # One for every trial with that specific stimuli
                start_time = trial_timestamps[0]
                stop_time = max(trial_timestamps)  # Some are 0 at the end so [-1] indexing does not work.
                data_dict = dict(
                    start_time=start_time, stop_time=stop_time, stimulus=stimulus, stimulus_name=stimulus_name
                )
                trial_dict_list.append(data_dict)

        # Order by starting time
        sorted_trial_dict_list = sorted(trial_dict_list, key=lambda x: x["start_time"])
        
        # Add extra columns, descriptions are taken from the provided Readme files with the data
        autor_description = f"is a string of the stimulus class, these include: 'benoptstim', 'looming', 'angular_velocity', 'sweeping_spot', 'adamstim', 'benstim'"
        nwbfile.add_trial_column(name="stimulus", description=autor_description)
        autor_description =  f"is a string of the specific stimulus"
        nwbfile.add_trial_column(name="stimulus_name", description=autor_description)

        [nwbfile.add_trial(**row_dict) for row_dict in sorted_trial_dict_list]

        # Df/F

        return nwbfile
