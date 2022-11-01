"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    MovieInterface,
)

from .interfaces import (
    Cowley2022MappingCourtshipPoseEstimationInterface,
    Cowley2022MappingCourtshipAudioInterface,
    Cowley2022MappingCourtshipAudioSegmentationInterface,
    Cowley2022MappingCourtshipStimuliInterface,
    Cowley2022MappingImagingMultipleInterface,
    Colwey2022MappingSegmentationInterface,
    Cowley2022MappingImagingBehaviorInterface,
    Cowley2022MappingImagingStimuliInterface,
)


class Cowley2022MappingCourtshipNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        PoseEstimation=Cowley2022MappingCourtshipPoseEstimationInterface,
        Audio=Cowley2022MappingCourtshipAudioInterface,
        AudioSegmentation=Cowley2022MappingCourtshipAudioSegmentationInterface,
        ReconstructedStimuli=Cowley2022MappingCourtshipStimuliInterface,
    )


class Cowley2022MappingImagingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Imaging=Cowley2022MappingImagingMultipleInterface,
        Segmentation=Colwey2022MappingSegmentationInterface,
        Behavior=Cowley2022MappingImagingBehaviorInterface,
        Stimuli=Cowley2022MappingImagingStimuliInterface,
    )
