from pathlib import Path
import pickle
import numpy as np

from roiextractors import SegmentationExtractor
from neuroconv.datainterfaces.ophys.basesegmentationextractorinterface import BaseSegmentationExtractorInterface


class Cowley2022MappingSegmentationExtractor(SegmentationExtractor):
    def __init__(self, responses_file_path: str, subject: str):
        # Point to data

        super().__init__()

        self.responses_file_path = Path(responses_file_path)
        assert self.responses_file_path.is_file()
        self.subject = subject

        with open(self.responses_file_path, "rb") as f:
            pickled_data = pickle.load(f, encoding="latin1")

        subject_data = [data for data in pickled_data if data["file_id"] == self.subject]

        ca_trace_and_timestamps = []
        for trial_data in subject_data:
            ca_trace_array = trial_data["ca_trace"]
            timestamps_array = trial_data["timepts"]
            for ca_trace, timestamps in zip(ca_trace_array, timestamps_array):
                ca_trace_and_timestamps.append((ca_trace, timestamps))

        first_timestamp = lambda x: x[1][0]
        sorted_ca_trace_and_timestamps = sorted(ca_trace_and_timestamps, key=first_timestamp)

        calcium_trace = np.concatenate([trace_time_tuple[0] for trace_time_tuple in sorted_ca_trace_and_timestamps])
        timestamps = np.concatenate([trace_time_tuple[1] for trace_time_tuple in sorted_ca_trace_and_timestamps])

        # Some of the timestamps and calcium traces data the end is 0s.
        # The timestamps do not start in 0
        calcium_trace = calcium_trace[timestamps > 0]
        timestamps = timestamps[timestamps > 0]

        # Set attributes
        self._times = timestamps

        self._roi_response_dff = calcium_trace[:, np.newaxis]  # To account for one roi/unit

        # Set image mask
        self._image_masks = np.ones(shape=(256, 256, 1))

    def get_image_size(self):

        return np.array((256, 265))

    def get_accepted_list(self):

        return [0]

    def get_rejected_list(self):

        return []


class Colwey2022MappingSegmentationInterface(BaseSegmentationExtractorInterface):

    Extractor = Cowley2022MappingSegmentationExtractor

    def __init__(self, responses_file_path: str, subject: str, verbose: str = True):
        super().__init__(responses_file_path=responses_file_path, subject=subject)
        self.verbose = verbose
