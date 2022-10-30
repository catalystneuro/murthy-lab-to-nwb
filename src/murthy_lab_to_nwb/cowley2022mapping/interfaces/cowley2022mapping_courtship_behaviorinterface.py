"""Primary class defining conversion of experiment-specific behavior."""
from pathlib import Path

import numpy as np
from scipy.io import loadmat
import pandas as pd

from pynwb.file import NWBFile, ProcessingModule
from neuroconv.basedatainterface import BaseDataInterface
from ndx_pose import PoseEstimationSeries, PoseEstimation
from ndx_events import LabeledEvents


class Cowley2022MappingCourtshipBehaviorInterface(BaseDataInterface):
    """My behavior interface docstring"""

    def __init__(self, file_path: str, video_file_path: str):

        self.sound_and_joints_data_path = Path(file_path)
        self.original_video_file_path = Path(video_file_path)
        assert self.sound_and_joints_data_path.is_file(), "joint joints and sound file not found"

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible
        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict):
        # All the custom code to write through PyNWB

        # Extract the data
        sound_and_joints_data = loadmat(self.sound_and_joints_data_path, squeeze_me=True)

        self.add_pose_estimation_to_nwb(nwbfile=nwbfile, sound_and_joints_data=sound_and_joints_data)

        self.add_song_behavior_to_nwb(nwbfile=nwbfile, sound_and_joints_data=sound_and_joints_data)

    def add_song_behavior_to_nwb(self, nwbfile, sound_and_joints_data):

        # Extract the sounds data
        pulse_times = sound_and_joints_data["pulse_times"]  # The timestamps of the pulse event
        pulse_types = sound_and_joints_data["pulse_types"]  # The type (0 is slow and 1 is fast)
        sine_present = sound_and_joints_data["sine_present"]  # A bolean array indicating presence of s

        # Extract slow and fast pulses timestamps
        pslow_mask = pulse_types == 0
        pfast_mask = ~pslow_mask
        slow_pulse_timestamps = pulse_times[pslow_mask] / 10000  # Transform to seconds
        fast_pulse_timestamps = pulse_times[pfast_mask] / 10000  # Transform to seconds
        # pulse_times[-1] / (60 * 10000) gives ~ 30 minutes which is the stated recorded time in the paper.

        # Extract sine timestamps
        frames_where_sine_is_present = np.where(sine_present == 1)[0]
        sampling_frequency = 30.0  # From readme in shared data and paper
        sine_timestamps = frames_where_sine_is_present / sampling_frequency

        # Prepare data for creating a LabeledEvent object
        label_to_number = {"slow_pulse": 0, "fast_pulse": 1, "sine": 2}
        sine_df = pd.DataFrame(sine_timestamps, columns=["timestamps"])
        sine_df["data"] = label_to_number["sine"]
        slow_pulse_df = pd.DataFrame(slow_pulse_timestamps, columns=["timestamps"])
        slow_pulse_df["data"] = label_to_number["slow_pulse"]
        fast_pulse_df = pd.DataFrame(fast_pulse_timestamps, columns=["timestamps"])
        fast_pulse_df["data"] = label_to_number["fast_pulse"]

        all_events_df = pd.concat([sine_df, slow_pulse_df, fast_pulse_df]).sort_values(by="timestamps")

        events = LabeledEvents(
            name="Male song events",
            description="Male song events extracted using audio segmentation",
            timestamps=all_events_df.timestamps.to_numpy(),
            resolution=1.0 / sampling_frequency,  # resolution of the timestamps
            data=all_events_df.data.to_numpy(),
            labels=list(label_to_number),
        )

        # Add a processing with the sound behavior to the nwb file
        processing_module_name = "Sound behavior"
        description = "Sound estimation extracted during courtship experiments"
        nwb_processing_song = nwbfile.create_processing_module(name=processing_module_name, description=description)
        nwb_processing_song.add(events)

        return nwbfile

    def add_pose_estimation_to_nwb(self, nwbfile, sound_and_joints_data):

        # Extract the joints data
        self.joints_data = sound_and_joints_data["joint_time_sex_position"]

        self.node_to_data_index = {"head": 0, "thorax": 1, "tail-abdomen": 2}
        self.sex_to_data_index = {"female": 0, "male": 1}
        self.position_to_index_amp = {"x": 0, "y": 1}

        # Add a processing module
        processing_module_name = "Pose estimation behavior"
        description = "Pose estimation behavior for sex and female flies in courtship experiments"
        nwb_processing_pose = nwbfile.create_processing_module(name=processing_module_name, description=description)

        # Add a container for the male and another for the female
        for sex in self.sex_to_data_index:
            pose_estimation_series_list = self.build_pose_estimation_list(sex)
            pose_estimation_container = self.build_pose_estimation_container(sex, pose_estimation_series_list)
            nwb_processing_pose.add(pose_estimation_container)

        return nwbfile

    def build_pose_estimation_list(self, sex):

        pose_estimation_series_list = []
        for node in self.node_to_data_index:

            node_trajectory = self.joints_data[self.node_to_data_index[node], :, self.sex_to_data_index[sex], :]
            node_trajectory = node_trajectory.repeat(2, axis=0)  # Increase frequency to video frequency

            scaling_factor = 25.0  # Slack exchange
            confidence = np.ones(node_trajectory.shape[0]) * np.nan  # TO-DO
            pose_estimation_series_list.append(
                PoseEstimationSeries(
                    name=f"{node}",
                    description=f"Sequential trajectory of {node}.",
                    data=node_trajectory * scaling_factor,  # Scale of given the author
                    confidence=confidence,
                    unit="pixels",
                    reference_frame="No reference.",
                    rate=60.0,  # From methods (30 x 2)
                )
            )

        return pose_estimation_series_list

    def build_pose_estimation_container(self, sex, pose_estimation_series_list):
        container_description = f"Pose estimation container for {sex} fly. Courtship experiments."

        video_relative_path = f"./{self.original_video_file_path.name}"

        pose_estimation_container = PoseEstimation(
            name=f"sex={sex}",
            pose_estimation_series=pose_estimation_series_list,
            description=container_description,
            original_videos=[video_relative_path],
            source_software="SLEAP",
            nodes=list(self.node_to_data_index.keys()),
            dimensions=np.array([[1280, 960]]).astype("uint64"),  # Extracted with ffprobe
        )

        return pose_estimation_container
