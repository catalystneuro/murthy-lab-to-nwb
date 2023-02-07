from typing import Union
import io

import pandas as pd
import numpy as np

import av
from ipywidgets import widgets
from IPython.display import Video, display
from skimage.draw import disk, line

from pynwb.base import TimeSeries, DynamicTable, ProcessingModule
from neuroconv.datainterfaces.behavior.video.video_utils import VideoCaptureContext


def extract_pose_estimation_data(pose_estimation_module: ProcessingModule) -> pd.DataFrame:
    all_tracks = pose_estimation_module.data_interfaces.keys()
    data_frames_list = []

    for track_name in all_tracks:
        track = pose_estimation_module[track_name]

        data_dict = {}
        for node in track.nodes:
            if track[node].rate:
                starting_time = track[node].starting_time if track[node].starting_time else 0
                node_timestamps = starting_time + np.arange(track[node].data.shape[0]) * 1.0 / track[node].rate

            else:
                node_timestamps = track[node].timestamps[:]

            width = track[node].data[:, 0]
            height = track[node].data[:, 1]

            data_dict["width"] = pd.Series(width, index=node_timestamps)
            data_dict["height"] = pd.Series(height, index=node_timestamps)
            data_dict["node"] = pd.Series([f"{node}"] * width.size, node_timestamps)
            data_dict["track"] = pd.Series([f"{track_name}"] * width.size, index=node_timestamps)

            node_df = pd.DataFrame(data_dict)
            data_frames_list.append(node_df)

    data_frames_list = (
        df.set_index(["track", "node"], append=True)
        .unstack(level=[1, 2])
        .swaplevel(0, 1, axis=1)
        .swaplevel(1, 2, axis=1)
        for df in data_frames_list
    )
    data_df = pd.concat(data_frames_list, axis=1, sort=True)

    return data_df


def draw_frame(frame, data_row):
    all_tracks = data_row.index.levels[0].values
    track_color_list = [(255, 0, 0), (0, 0, 255)]

    for track_index, track_name in enumerate(all_tracks):
        data_row_track = data_row[f"{track_name}"]
        track_color = track_color_list[track_index]
        frame = draw_track(frame, data_row_track, node_color=track_color)
    return frame


def draw_track(frame, data_row, node_color):
    all_nodes = data_row.index.levels[0]
    for node in all_nodes:
        width = data_row[f"{node}"]["width"]
        height = data_row[f"{node}"]["height"]
        if not np.isnan(width):
            length = 5
            rr, cc = disk((height, width), length, shape=frame.shape)
            frame[rr, cc, :] = node_color
    return frame


def generate_in_memory_video(
    source_video_file_path,
    data_df,
    start_frame,
    end_frame,
    frame_offset=0,
):
    # frame_index_to_frame_function = lambda frame_index: video_reader[frame_index]
    frame_range = range(start_frame, end_frame)
    with VideoCaptureContext(file_path=str(source_video_file_path)) as video_context:
        frame_index_to_frame_function = lambda frame_index: video_context.get_video_frame(frame_number=frame_index)
        frames_for_video = [
            draw_frame(
                frame=frame_index_to_frame_function(frame_index),
                data_row=data_df.iloc[frame_index + frame_offset],
            )
            for frame_index in frame_range
        ]

        # Get video information
        image_shape = video_context.get_frame_shape()
        frame_rate = video_context.get_video_fps()

    # Make video
    in_memory_video_file = io.BytesIO()
    new_container = av.open(in_memory_video_file, mode="w", format="mp4")
    new_stream = new_container.add_stream("h264", rate=frame_rate)

    new_stream.options = {"crf": "35"}  # Some reasonable speed-quality trade-off
    new_stream.width = image_shape[1]
    new_stream.height = image_shape[0]

    for frame in frames_for_video:
        encoded_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        for packet in new_stream.encode(encoded_frame):
            new_container.mux(packet)

    # Flush stream
    for packet in new_stream.encode():
        new_container.mux(packet)

    # Close the file
    new_container.close()

    return in_memory_video_file


def generate_video_to_display(source_video_file_path, data_df, start_frame, end_frame, frame_offset):
    with VideoCaptureContext(file_path=str(source_video_file_path)) as video_context:
        image_shape = video_context.get_frame_shape()
        frame_rate = video_context.get_video_fps()

    # Transform from seconds to frame number
    start_frame = int(start_frame * frame_rate)
    end_frame = int(end_frame * frame_rate)
    frame_offset = int(frame_offset * frame_rate)

    in_memory_video = generate_in_memory_video(
        source_video_file_path=source_video_file_path,
        data_df=data_df,
        start_frame=start_frame,
        end_frame=end_frame,
        frame_offset=frame_offset,
    )

    scale = 0.50  # Chosing the size to display in the notebook
    video_width = int(image_shape[1] * scale)
    video_heigth = int(image_shape[0] * scale)

    displayed_video = Video(
        data=in_memory_video.getvalue(), width=video_width, height=video_heigth, embed=True, mimetype="video/mp4"
    )
    return displayed_video


class PoseEstimationWidgetController(widgets.VBox):
    def __init__(self):
        super().__init__()

        self.start_frame_widget = widgets.FloatText(value=0, description="Start time (s):", disabled=False)

        self.end_frame_widget = widgets.FloatText(value=1, description="End time (s)", disabled=False)

        self.frame_offset_widget = widgets.FloatText(value=0, description="Time offset (s)", disabled=False)

        self.children = [self.start_frame_widget, self.end_frame_widget, self.frame_offset_widget]

    @property
    def start_frame(self):
        return self.start_frame_widget.value

    @property
    def end_frame(self):
        return self.end_frame_widget.value

    @property
    def frame_offset(self):
        return self.frame_offset_widget.value


class PoseEstimationWidget(widgets.HBox):
    def __init__(self, pose_estimation_module, video_file_path):
        super().__init__()

        self.data_df = extract_pose_estimation_data(pose_estimation_module)
        self.video_file_path = video_file_path

        self.controller = PoseEstimationWidgetController()
        self.plot_button = widgets.Button(description="Load video")
        self.all_controls = widgets.VBox([self.controller, self.plot_button])

        self.display_widget = widgets.Output(layout={"border": "1px solid black"})
        self.display_widget.append_stdout("Select interval to load pose estimation annotated video")

        self.children = [self.all_controls, self.display_widget]

        self.plot_button.on_click(self.button_action)

    def button_action(self, button_instance):
        start_frame = self.controller.start_frame
        end_frame = self.controller.end_frame
        frame_offset = self.controller.frame_offset
        self.display_widget.clear_output(wait=True)

        with self.display_widget:
            display(
                generate_video_to_display(
                    source_video_file_path=self.video_file_path,
                    data_df=self.data_df,
                    start_frame=start_frame,
                    end_frame=end_frame,
                    frame_offset=frame_offset,
                )
            )
