"""Primary class defining conversion of experiment-specific behavior."""
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from pynwb.file import NWBFile, ProcessingModule
from neuroconv.basedatainterface import BaseDataInterface
from ndx_pose import PoseEstimationSeries, PoseEstimation


class Cowley2022MappingCourtshipPoseEstimationInterface(BaseDataInterface):
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
