"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter
from neuroconv.datainterfaces import (
    MovieInterface,
)

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingBehaviorInterface


class Cowley2022MappingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Movie=MovieInterface,
        Behavior=Cowley2022MappingBehaviorInterface,
    )
