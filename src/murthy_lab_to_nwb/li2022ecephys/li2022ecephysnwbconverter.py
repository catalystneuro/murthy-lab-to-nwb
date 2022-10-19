"""Primary NWBConverter class for this dataset."""

from neuroconv import NWBConverter


from .li2022ecephysinterface import Li2022EcephysInterface


class Li2022EcephysNWBConverter(NWBConverter):
    """Primary conversion class for my extracellular electrophysiology dataset."""

    data_interface_classes = dict(
        Ecephys=Li2022EcephysInterface,
    )
