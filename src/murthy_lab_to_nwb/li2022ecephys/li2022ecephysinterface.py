from pathlib import Path

import h5py

from spikeinterface.extractors import NumpyRecording

from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface
from neuroconv.utils import get_schema_from_hdmf_class
from pynwb.ecephys import ElectricalSeries


class Li2022EcephysInterface(BaseRecordingExtractorInterface):

    Extractor = NumpyRecording

    def __init__(self, file_path: str, verbose: bool = True):

        self.file = h5py.File(file_path, "r")
        self.header = self.file["header"]

        traces_name_list = sorted([key for key in self.file.keys() if "sweep" in key])

        channel_ids = self.header["AIChannelNames"][()]
        traces_list = [self.file[trace_name]["analogScans"][()].T for trace_name in traces_name_list]
        t_starts = [self.file[trace_name]["timestamp"][()] for trace_name in traces_name_list]
        sampling_frequency = self.header["AcquisitionSampleRate"][0, 0]

        super().__init__(
            verbose=verbose,
            traces_list=traces_list,
            sampling_frequency=sampling_frequency,
            t_starts=t_starts,
            channel_ids=channel_ids,
        )
        self.recording_extractor

        channel_units = self.header["AIChannelUnits"][()]
        gains = 1.0 / self.header["AIChannelScales"][()].flatten()
        self.recording_extractor.set_channel_gains(gains)
        self.recording_extractor.set_channel_offsets(offsets=0)
        self.recording_extractor.set_property(key="channel_units", values=channel_units.astype("str"))

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
        conversion_options = dict(write_as="processed", stub_test=False)
        return conversion_options
