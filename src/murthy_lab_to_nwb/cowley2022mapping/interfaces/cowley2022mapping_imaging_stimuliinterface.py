"""Primary class for adding stimuli to the imaging experiment in cowley 2022."""
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
import numpy as np

from neuroconv.basedatainterface import BaseDataInterface


class Cowley2022MappingImagingStimuliInterface(BaseDataInterface):
    def __init__(self, stimuli_folder_path: str):

        self.stimuli_folder_path = Path(stimuli_folder_path)
        assert self.stimuli_folder_path.is_dir(), f"{self.stimuli_folder_path} not a directory/folder"

    def get_metadata(self):
        # Automatically retrieve as much metadata as possible

        return dict()

    def run_conversion(self, nwbfile: NWBFile, metadata: dict):
        # All the custom code to write through PyNWB

        for zip_file_path in self.stimuli_folder_path.iterdir():
            if not is_zipfile(zip_file_path):
                warning_string = f"file {zip_file_path.name} is not zip, skipping it"
                warn(warning_string)
                continue
            image_series = self.create_image_series_for_stimuli(zip_file_path=zip_file_path)
            nwbfile.add_stimulus(image_series)

        return nwbfile

    def create_image_series_for_stimuli(self, zip_file_path: Union[Path, str]):
        assert is_zipfile(zip_file_path), "file_does not point to a zip"
        zip_file = ZipFile(zip_file_path)

        file_bytes_list = (zip_file.read(name=name) for name in natsorted(zip_file.namelist()))
        pillow_image_list = (Image.open(fp=BytesIO(file_bytes)) for file_bytes in file_bytes_list)

        image_list = [np.asarray(pic) for pic in pillow_image_list]
        image_data = np.array(image_list)

        name = zip_file_path.stem
        rate = 60.0  # Hz
        unit = "values between 0 and 255"
        image_series = ImageSeries(name=name, description=name, data=image_data, rate=rate, unit=unit)

        return image_series
