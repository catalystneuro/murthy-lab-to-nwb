from pathlib import Path

from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from roiextractors.multiimagingextractor import MultiImagingExtractor
from roiextractors import ScanImageTiffImagingExtractor


class Cowley2022MappingImagingMultipleInterface(BaseImagingExtractorInterface):
    Extractor = MultiImagingExtractor

    def __init__(self, subject: str, tiff_dir_path: str, sampling_frequency: float):

        tiff_dir_path = Path(tiff_dir_path)
        subject_tiff_files = [path for path in tiff_dir_path.iterdir() if path.stem[:10] == subject]
        subject_tiff_files_sorted = sorted(subject_tiff_files, key=lambda x: x.stem)

        imaging_extractors = [
            ScanImageTiffImagingExtractor(file_path=str(file_path), sampling_frequency=sampling_frequency)
            for file_path in subject_tiff_files_sorted
        ]
        super().__init__(imaging_extractors=imaging_extractors)
