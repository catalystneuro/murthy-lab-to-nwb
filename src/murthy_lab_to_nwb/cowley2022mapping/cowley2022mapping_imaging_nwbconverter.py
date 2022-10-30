"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter

from .interfaces import (
    Cowley2022MappingImagingBehaviorInterface,
    Cowley2022MappingImagingMultipleInterface,
    Colwey2022MappingSegmentationInterface,
    Cowley2022MappingImagingStimuliInterface,
)


class Cowley2022MappingImagingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Imaging=Cowley2022MappingImagingMultipleInterface,
        Segmentation=Colwey2022MappingSegmentationInterface,
        Behavior=Cowley2022MappingImagingBehaviorInterface,
        Stimuli=Cowley2022MappingImagingStimuliInterface,
    )
