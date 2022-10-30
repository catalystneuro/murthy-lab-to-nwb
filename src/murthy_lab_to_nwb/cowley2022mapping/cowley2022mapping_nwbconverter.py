"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    MovieInterface,
)

from .interfaces import (
    Cowley2022MappingCourtshipBehaviorInterface,
    Cowley2022MappingCourtshipAudioInterface,
    Cowley2022MappingImagingBehaviorInterface,
    Cowley2022MappingImagingMultipleInterface,
    Colwey2022MappingSegmentationInterface,
    Cowley2022MappingImagingStimuliInterface,
)


class Cowley2022MappingCourtshipNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        Audio=Cowley2022MappingCourtshipAudioInterface,
        Behavior=Cowley2022MappingCourtshipBehaviorInterface,
    )


class Cowley2022MappingImagingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Imaging=Cowley2022MappingImagingMultipleInterface,
        Segmentation=Colwey2022MappingSegmentationInterface,
        Behavior=Cowley2022MappingImagingBehaviorInterface,
        Stimuli=Cowley2022MappingImagingStimuliInterface,
    )
