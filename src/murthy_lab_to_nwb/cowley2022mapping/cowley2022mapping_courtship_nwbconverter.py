"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    MovieInterface,
)

from .interfaces import Cowley2022MappingCourtshipBehaviorInterface, Cowley2022MappingCourtshipAudioInterface


class Cowley2022MappingCourtshipNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        Audio=Cowley2022MappingCourtshipAudioInterface,
        Behavior=Cowley2022MappingCourtshipBehaviorInterface,
    )