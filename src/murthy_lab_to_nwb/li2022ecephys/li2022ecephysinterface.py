from pathlib import Path

import h5py

from spikeinterface.extractors import NumpyRecording

from neuroconv.datainterfaces.ecephys.baserecordingextractorinterface import BaseRecordingExtractorInterface


class Li2022EcephysInterface(BaseRecordingExtractorInterface):

    Extractor = NumpyRecording

    def __init__(self, file_path: str, verbose: bool = True):

        file = h5py.File(file_path, "r")
        header = file["header"]

        traces_name_list = sorted([key for key in file.keys() if "sweep" in key])

        channel_ids = header["AIChannelNames"][()]
        traces_list = [file[trace_name]["analogScans"][()].T for trace_name in traces_name_list]
        t_starts = [file[trace_name]["timestamp"][()] for trace_name in traces_name_list]
        sampling_frequency = file["header"]["AcquisitionSampleRate"][()]

        super().__init__(
            verbose=verbose,
            traces_list=traces_list,
            sampling_frequency=sampling_frequency,
            t_starts=t_starts,
            channel_ids=channel_ids,
        )
        self.recording_extractor

        channel_units = header["AIChannelUnits"][()]
        gains = 1.0 / header["AIChannelScales"][()]
        self.recording_extractor.set_channel_gains(gains)
        self.recording_extractor.set_channel_offsets(offsets=0)
        self.recording_extractor.set_property(key="channel_units", values=channel_units.astype("str"))

    def get_conversion_options(self):
        conversion_options = dict(write_as="processed", es_key="ElectricalSeriesProcessed", stub_test=False)
        return conversion_options
