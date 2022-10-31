"""Primary class for adding reconstructed stimuli to the courtship experiment in cowley 2022."""
from pathlib import Path
from typing import Union
from io import BytesIO
from zipfile import ZipFile, is_zipfile
from warnings import warn
import pickle

from PIL import Image
from natsort import natsorted
from pynwb.file import NWBFile
from pynwb.image import ImageSeries
from hdmf.backends.hdf5.h5_utils import H5DataIO
import numpy as np

from neuroconv.basedatainterface import BaseDataInterface


class Cowley2022MappingCourtshipStimuliInterface(BaseDataInterface):
    def __init__(self, zip_file_path: str):

        self.zip_file_path = Path(zip_file_path)
        assert self.zip_file_path.is_file(), f"{self.zip_file_path} not found"

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible

        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict, stub_test: bool = False):
        # All the custom code to write through PyNWB

        image_series = self.create_image_series_for_reconstructed_stimuli(
            zip_file_path=self.zip_file_path, stub_test=stub_test
        )
        nwbfile.add_stimulus(image_series)
        return nwbfile

    def create_image_series_for_reconstructed_stimuli(self, zip_file_path: Union[Path, str], stub_test: bool = False):
        assert is_zipfile(zip_file_path), "file_does not point to a zip"
        zip_file = ZipFile(zip_file_path)

        file_bytes_list = (zip_file.read(name=name) for name in natsorted(zip_file.namelist()))
        if stub_test:
            file_bytes_list = (zip_file for index, zip_file in enumerate(file_bytes_list) if index < 10)

        pillow_image_list = (Image.open(fp=BytesIO(file_bytes)) for file_bytes in file_bytes_list)

        image_list = [np.asarray(pic) for pic in pillow_image_list]
        image_data = np.array(image_list)

        name = "reconstructed_stimuli"
        description = "artificial reconstructed stimuli as seen by the male fly"
        rate = 30.0  # Hz  (makes for reconstructed stimuli of approximately 30 minutes, as the movie)
        unit = "values between 0 and 255"
        wrapped_data = H5DataIO(data=image_data, compression="gzip", compression_opts=6)
        image_series = ImageSeries(name=name, description=description, data=wrapped_data, rate=rate, unit=unit)

        return image_series
