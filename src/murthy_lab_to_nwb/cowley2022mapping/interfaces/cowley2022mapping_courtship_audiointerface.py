"""Data interface for the audio data in this conversion."""
from pathlib import Path

from scipy.io import loadmat


from pynwb.file import NWBFile, ProcessingModule
from neuroconv.basedatainterface import BaseDataInterface
from ndx_sound import AcousticWaveformSeries


class Cowley2022MappingCourtshipAudioInterface(BaseDataInterface):
    """My behavior interface docstring"""

    def __init__(self, file_path: str):

        self.audio_file_path = Path(file_path)
        assert self.audio_file_path.is_file(), "file with audio data not found"

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible
        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        # All the custom code to write through PyNWB
        audio_dict = loadmat(self.audio_file_path, squeeze_me=True)
        audio_data = audio_dict["data"]  # This dat is int16

        conversion = 1.0 / audio_dict["dataScalingFactor"]
        # This will cast return the value in floats

        if stub_test:
            audio_data = audio_data[:100]  # First 100 samples just for testing

        description = (
            ". Each recording chamber had a floor lined with white plastic mesh and equipped with 16 microphones"
            "The description of the recording system is referenced to be found on: \n"
            "1) doi: 10.1186/1741-7007-11-11.\n"
            "2) doi: 10.1016/j.cub.2018.06.011. Epub 2018 Jul 26."
        )

        device_dict = dict(name="Microphone", description=description)
        nwbfile.create_device(**device_dict)

        # Create AcousticWaveformSeries with ndx-sound
        acoustic_waveform_series = AcousticWaveformSeries(
            name="audio_waveforms",
            data=audio_data,
            rate=10.0,
            description="acoustic stimulus",
            conversion=conversion,
        )

        nwbfile.add_acquisition(acoustic_waveform_series)
