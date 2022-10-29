from pathlib import Path

import h5py
import numpy as np

from spikeinterface.extractors import NumpyRecording
from spikeinterface.core import BaseRecording, BaseRecordingSegment
from pynwb.ecephys import ElectricalSeries

from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from neuroconv.utils import get_schema_from_hdmf_class


class Li2022EcephysRecordingSegment(BaseRecordingSegment):
    def __init__(self, traces, sampling_frequency, t_start):
        BaseRecordingSegment.__init__(self, sampling_frequency=sampling_frequency, t_start=t_start)
        self._traces = traces

    def get_num_samples(self):
        return self._traces.shape[1]

    def get_num_channels(self):
        return self._traces.shape[0]

    def get_traces(self, start_frame, end_frame, channel_indices):
        # Traces are channels wavesurfer format is channels x time
        traces = self._traces[:, start_frame:end_frame]

        # Scaling traces, see the notes on:
        # https://wavesurfer.janelia.org/manual-0.945/index.html#reading-acquired-data
        scaled_traces = np.empty(traces.shape)
        for i in range(0, self.get_num_channels()):
            scaled_traces[i, :] = np.polyval(np.flipud(self.analog_scaling_coefficients[i, :]), traces[i, :])

        traces = scaled_traces.T
        if channel_indices is not None:
            traces = traces[:, channel_indices]

        return traces


class Li2022EcephysRecording(BaseRecording):
    """


    Parameters
    ----------
    file_path: the fille path to the wavesurfer hdf5 file
    """

    is_writable = False

    def __init__(self, file_path: str):

        self.file = h5py.File(file_path, "r")
        self.header = self.file["header"]

        # Extract the traces lazily in the wavesurfer format
        traces_name_list = sorted([key for key in self.file.keys() if "sweep" in key])
        traces_list = [self.file[trace_name]["analogScans"] for trace_name in traces_name_list]

        # AI stands for analog input in the surf format
        channel_ids = (self.header["AIChannelNames"][()]).astype("str")
        if channel_ids is None:
            channel_ids = np.arange(traces_list[0].shape[0])
        else:
            channel_ids = np.asarray(channel_ids)
            assert channel_ids.size == traces_list[0].shape[0]

        # The t-starts are represent as a single time stamp for every sweep
        t_starts = [self.file[trace_name]["timestamp"][()] for trace_name in traces_name_list]
        assert len(t_starts) == len(traces_list), "t_starts must be a list of same size than traces_list"
        if t_starts is not None:
            t_starts = [float(t_start) for t_start in t_starts]

        sampling_frequency = float(self.header["AcquisitionSampleRate"][0, 0])

        # Dtype
        dtype = traces_list[0].dtype
        assert all(dtype == ts.dtype for ts in traces_list)

        # Polyonomial scaling
        self.analog_scaling_coefficients = self.header["AIScalingCoefficients"]

        BaseRecording.__init__(self, sampling_frequency, channel_ids, dtype)
        self.is_dumpable = False

        for i, traces in enumerate(traces_list):
            if t_starts is None:
                t_start = None
            else:
                t_start = t_starts[i]
            rec_segment = Li2022EcephysRecordingSegment(traces, sampling_frequency, t_start)
            rec_segment.analog_scaling_coefficients = self.analog_scaling_coefficients
            self.add_recording_segment(rec_segment)

        gains = 1.0 / self.header["AIChannelScales"][()].flatten()
        self.set_channel_gains(gains)
        self.set_channel_offsets(offsets=0)

        channel_units = self.header["AIChannelUnits"][()]
        self.set_property(key="channel_units", values=channel_units.astype("str"))

        self._kwargs = {
            "traces_list": traces_list,
            "t_starts": t_starts,
            "sampling_frequency": sampling_frequency,
        }


class Li2022EcephysInterface(BaseRecordingExtractorInterface):

    Extractor = Li2022EcephysRecording

    def __init__(self, file_path: str, verbose: bool = True):

        super().__init__(verbose=verbose, file_path=file_path)

    # def get_metadata_schema(self):
    #     metadata_schema = super().get_metadata_schema()

    #     metadata_schema["properties"]["Ecephys"]["properties"].update(
    #         ElectricalSeriesProcessed=get_schema_from_hdmf_class(ElectricalSeries)
    #     )
    #     return metadata_schema

    # def get_metadata(self):
    #     metadata = super().get_metadata()

    #     metadata["Ecephys"]["ElectricalSeriesProcessed"] = dict(
    #         name="ElectricalSeriesProcessed", description="Processed data from wavesurfer"
    #     )

    #     return metadata

    def get_conversion_options(self):
        conversion_options = dict(write_as="processed", iterator_type="v2", stub_test=False)
        return conversion_options
