"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter

from murthy_lab_to_nwb.cowley2022mapping_imaging import Cowley2022MappingImagingMultipleInterface
from murthy_lab_to_nwb.cowley2022mapping_imaging import Cowley2022MappingImagingBehaviorInterface


class Cowley2022MappingImagingNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Imaging=Cowley2022MappingImagingMultipleInterface,
        Behavior=Cowley2022MappingImagingBehaviorInterface,
    )
