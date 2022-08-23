"""Primary NWBConverter class for this dataset."""
from neuroconv import (
    NWBConverter,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    PhySortingInterface,
)

from murthy_lab_to_nwb.cowley2022mapping import Cowley2022MappingBehaviorInterface


class Cowley2022MappingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Recording=SpikeGLXRecordingInterface,
        LFP=SpikeGLXLFPInterface,
        Sorting=PhySortingInterface,
        Behavior=Cowley2022MappingBehaviorInterface,
    )
