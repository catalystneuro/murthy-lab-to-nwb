from pathlib import Path

from natsort import natsorted


from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import (
    BaseImagingExtractorInterface,
)
from roiextractors.multiimagingextractor import MultiImagingExtractor
from roiextractors import ScanImageTiffImagingExtractor


class Cowley2022MappingImagingMultipleInterface(BaseImagingExtractorInterface):
    Extractor = MultiImagingExtractor

    def __init__(self, subject_tiff_files_dir_path: str, sampling_frequency: float):
        subject_tiff_files_dir_path = Path(subject_tiff_files_dir_path)
        assert subject_tiff_files_dir_path.is_dir(), f"{subject_tiff_files_dir_path} is not a folder / directory"
        subject_tiff_files = [path for path in subject_tiff_files_dir_path.iterdir()]
        subject_tiff_files_sorted = natsorted(subject_tiff_files, key=lambda x: x.stem)
        imaging_extractors_list = list()
        for file_path in subject_tiff_files_sorted:
            try:
                imaging_extractor = ScanImageTiffImagingExtractor(
                    file_path=str(file_path), sampling_frequency=sampling_frequency
                )
            except:
                raise ValueError(f"{file_path} could not be oppened by ScanImage")
            imaging_extractors_list.append(imaging_extractor)

        super().__init__(imaging_extractors=imaging_extractors_list)
