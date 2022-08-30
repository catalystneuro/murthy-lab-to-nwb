"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    MovieInterface,
)

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingBehaviorInterface 
from .cowley2022mappingaudiointerface import Cowley2022MappingAudioInterface


class Cowley2022MappingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        Audio=Cowley2022MappingAudioInterface,
        Behavior=Cowley2022MappingBehaviorInterface,
    )
