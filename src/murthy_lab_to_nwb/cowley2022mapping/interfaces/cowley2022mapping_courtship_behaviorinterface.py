"""Primary class defining conversion of experiment-specific behavior."""
from pathlib import Path
import pickle

import numpy as np
import pandas as pd

from pynwb.file import NWBFile, ProcessingModule
from pynwb import TimeSeries
from neuroconv.basedatainterface import BaseDataInterface
from ndx_events import LabeledEvents


class Cowley2022MappingCourtshipBehaviorInterface(BaseDataInterface):
    """My behavior interface docstring"""

    def __init__(self, file_path: str):

        self.file_path = Path(file_path)
        assert self.file_path.is_file(), f"male behavior data {file_path} not found"

        self.sound_and_joints_data_path = Path(file_path)

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible
        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict):
        # All the custom code to write through PyNWB

        # Extract the data
        unpickleFile = open(self.file_path, "rb")
        behavior_data = pickle.load(unpickleFile, encoding="latin1")

        # Add audio segmentation
        self.add_song_behavior_to_nwb(nwbfile=nwbfile, behavior_data=behavior_data)
        self.add_male_behavior_time_series(nwbfile=nwbfile, behavior_data=behavior_data)

    def add_song_behavior_to_nwb(self, nwbfile, behavior_data):

        sample_rate = 30.0  # number of frames /(60 * 30) is equal to 30 min which is the length of the videos
        sine_song_frames = np.nonzero(behavior_data["sine_bits"] == 1)[0]
        sine_timestamps = sine_song_frames / sample_rate

        slow_pulse_frames = np.nonzero(behavior_data["pslow_pulse_bits"] == 1)[0]
        slow_pulse_timestamps = slow_pulse_frames / sample_rate

        fast_pulse_frames = np.nonzero(behavior_data["pfast_pulse_bits"] == 1)[0]
        fast_pulse_timestamps = fast_pulse_frames / sample_rate

        # Prepare data for creating a LabeledEvent object
        label_to_number = {"slow_pulse": 0, "fast_pulse": 1, "sine": 2}
        sine_df = pd.DataFrame(sine_timestamps, columns=["timestamps"])
        sine_df["event"] = label_to_number["sine"]
        slow_pulse_df = pd.DataFrame(slow_pulse_timestamps, columns=["timestamps"])
        slow_pulse_df["event"] = label_to_number["slow_pulse"]
        fast_pulse_df = pd.DataFrame(fast_pulse_timestamps, columns=["timestamps"])
        fast_pulse_df["event"] = label_to_number["fast_pulse"]

        all_events_df = pd.concat([sine_df, slow_pulse_df, fast_pulse_df]).sort_values(by="timestamps")

        resolution = 1 / sample_rate  # resolution of the timestamp
        events = LabeledEvents(
            name="Male song events",
            description="Male song events extracted using audio segmentation",
            timestamps=all_events_df.timestamps.to_numpy(),
            resolution=resolution,
            data=all_events_df.event.to_numpy(),
            labels=list(label_to_number),
        )

        # Add a processing with the sound behavior to the nwb file
        processing_module_name = "Audio segmentation"
        description = "Sound behavioral segmentation extracted from microphones during courtship experiments"
        nwb_processing_song = nwbfile.create_processing_module(name=processing_module_name, description=description)
        nwb_processing_song.add(events)

        return nwbfile

    def add_male_behavior_time_series(self, nwbfile, behavior_data):
        sample_rate = 30.0  # number of frames /(60 * 30) is equal to 30 min which is the length of the videos

        # Provided by the author
        description_dict = {
            "orientation_changes": "angular velocity, between -180 and 180 where 0 indicates no change in head direction",
            "forward_vels": "velocity of male fly along the male fly's head direction. in units (mm/frame). positive --> forward, negative --> backwards",
            "lateral_vels": "velocity of male fly along the direction orthogonal to male fly's head direction in units (mm/frame). positive --> to the right, negative",
            "pfast_pulse_bits": "boolean indicator if a pfast pulse song is present or not per frame. 1 ",
            "pfast_pulse_amplitudes": "pfast pulse amplitude; not used in paper",
            "pslow_pulse_bits": "boolean indicator if a pslow pulse song is present or not per frame",
            "pslow_pulse_amplitudes": "pfast pulse amplitude; not used in paper",
            "sine_bits": "boolean indicator if a sine song is present or not per frame. 1",
            "female_widths": "size of fictive female viewed by the male. based on joint positions of male and female used as one of the parameters to reconstruct the fictive female",
            "female_orientations": " rotation of fictive female viewed by the male. based on joint positions of male and female. used as one of the parameters to reconstruct the fictive female. 0 degrees --> female faces away from male 90 degrees --> female faces to the right of the male (i.e., based on the male's view, the female's tail is to the left and the female's head is to the right) -90 degrees --> female faces to the left of the male (opposite of 90 degrees) -180/180 --> female faces towards the male",
            "female_lateral_positions": " position of fictive female. based on joint positions of male and female. used as one of the parameters to reconstruct the fictive female. between -1 and 1.  0 --> female is directly in front. -1/1 --> female is directly behind the male 0.5 --> female is directly to the right of the male -0.5 --> female is directly to the left of the male. Note that female_orientations and female_lateral_positions are separate: The female can be to the right of the male (lateral position = 0.5) but be facing to the left of the male (female orientation=-90). It also helps to think about the visual scene as wrapped around a cylinder (not a flat plane).,",
        }

        # Add a processing module for this behavior
        processing_module_name = "Male behavior"
        description = "Module with reconstructed time series of the male movements. Used in the paper for reconstruction of the male fly stimuli and network training"
        nwb_processing_behavior = nwbfile.create_processing_module(name=processing_module_name, description=description)

        # Exclude as these are added as events, a more appropiate format.
        audio_segmentation_keys = ["sine_bits", "pfast_pulse_bits", "pslow_pulse_bits"]
        behavior_to_time_series = [column for column in behavior_data.keys() if column not in audio_segmentation_keys]
        for behavior_key in behavior_to_time_series:
            data = behavior_data[behavior_key]
            name = behavior_key
            description = description_dict[behavior_key]

            time_series = TimeSeries(name=name, data=data, description=description, rate=sample_rate, unit="n.a.")
            nwb_processing_behavior.add(time_series)

        return nwbfile
