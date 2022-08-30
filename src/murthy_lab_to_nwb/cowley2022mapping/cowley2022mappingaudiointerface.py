"""Data interface for the audio data in this conversion."""
from pathlib import Path

from scipy.io import loadmat


from pynwb.file import NWBFile, ProcessingModule
from neuroconv.basedatainterface import BaseDataInterface
from ndx_sound import AcousticWaveformSeries


class Cowley2022MappingAudioInterface(BaseDataInterface):
    """My behavior interface docstring"""

    def __init__(self, subject: str, lobula_columnar_neuron_cell_line: str, data_dir_path: str):

        audio_dir_path = Path(data_dir_path) / "raw_data" / "courtship_behavior" / "audio"
        # 161101_10a05bin.mat
        padded_subject = subject[3:].rjust(2, "0")
        audio_string = f"{lobula_columnar_neuron_cell_line[2:]}{padded_subject}"
        audio_path = next(path for path in audio_dir_path.iterdir() if audio_string in path.stem)
        self.audio_file_path = audio_dir_path / audio_path
        assert self.audio_file_path.is_file(), "file with audio data not found"

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible
        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        # All the custom code to write through PyNWB
        audio_dict = loadmat(self.audio_file_path, squeeze_me=True)
        audio_data = audio_dict["data"] # This dat is int16

        conversion = 1.0 / audio_dict["dataScalingFactor"]
        # This will cast return the value in floats

        if stub_test:
            audio_data = audio_data[:100]  # First 100 samples just for testing

        # Create AcousticWaveformSeries with ndx-sound
        acoustic_waveform_series = AcousticWaveformSeries(
            name="audio_waveforms",
            data=audio_data,
            rate=30.0,  # TODO confirm with authors
            description="acoustic stimulus",
            unit="not_clear",  # TODO ask authors
            conversion=conversion,
        )

        nwbfile.add_acquisition(acoustic_waveform_series)
