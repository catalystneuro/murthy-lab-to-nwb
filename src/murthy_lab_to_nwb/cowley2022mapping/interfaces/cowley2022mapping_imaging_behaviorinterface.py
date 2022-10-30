"""Primary class defining conversion of experiment-specific behavior."""
from pathlib import Path
import pickle

import numpy as np

from pynwb.file import NWBFile, ProcessingModule
from pynwb.ophys import DfOverF, RoiResponseSeries

from neuroconv.basedatainterface import BaseDataInterface


class Cowley2022MappingImagingBehaviorInterface(BaseDataInterface):
    """Behavior interface conversion"""

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

        # Get the data types of the data
        type_to_columns = dict()
        for trial_data in subject_data:
            for key, value in trial_data.items():
                value_type = type(value)
                if value_type not in type_to_columns:
                    type_to_columns[value_type] = set()

                type_to_columns[value_type].add(key)

        float_columns = type_to_columns[np.float32]
        excluded_array = ["ca_trace", "timepts"]  # Already in the nwb-file
        array_columns = [column for column in type_to_columns[np.ndarray] if column not in excluded_array]

        # Add trials
        trial_dict_list = []
        for trial_data in subject_data:

            real_values_dict = {column: trial_data.get(column, np.nan) for column in float_columns}
            array_values_dict = {column: trial_data.get(column, None) for column in array_columns}

            stimulus = trial_data["stimulus"]
            timestamps = trial_data["timepts"]
            for index, trial_timestamps in enumerate(timestamps):  # One for every trial with that specific stimuli
                start_time = trial_timestamps[0]
                stop_time = max(trial_timestamps)  # Some are 0 at the end so [-1] indexing does not work.

                # Stimuli is either artificial or characterized with its simulation values
                stimulus_name = trial_data.get("stim_name", "None")

                # Add basic info
                data_dict = dict(
                    start_time=start_time,
                    stop_time=stop_time,
                    stimulus=stimulus,
                    stimulus_name=stimulus_name,
                )

                # Add real values to row
                data_dict.update(real_values_dict)

                # Add array values to row
                array_values_dict_per_sub_trial = {
                    column: list(data[index, :]) for column, data in array_values_dict.items()
                }
                data_dict.update(array_values_dict_per_sub_trial)

                trial_dict_list.append(data_dict)

        # Order by starting time
        sorted_trial_dict_list = sorted(trial_dict_list, key=lambda x: x["start_time"])

        # Add extra columns, descriptions are taken from the provided Readme files with the data
        autor_description = f"is a string of the stimulus class, these include: 'benoptstim', 'looming', 'angular_velocity', 'sweeping_spot', 'adamstim', 'benstim'"
        nwbfile.add_trial_column(name="stimulus", description=autor_description)
        autor_description = f"is a string of the specific stimulus"
        nwbfile.add_trial_column(name="stimulus_name", description=autor_description)

        for column in float_columns:
            nwbfile.add_trial_column(name=column, description=column)

        for column in array_columns:
            nwbfile.add_trial_column(name=column, description=column, index=True)

        [nwbfile.add_trial(**row_dict) for row_dict in sorted_trial_dict_list]

        return nwbfile
