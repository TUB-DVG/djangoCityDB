"""This module contains the class HeatExchanger from EnergyADE."""
from citydb.modules.energy.energysystems.energysystem import EnergyConversionSystem
from django.contrib.gis.db import models


class HeatExchanger(EnergyConversionSystem):
    """ORM class for heat_exchanger table from EnergyADE.

    Heat exchanger to model the connection to a district heating or cooling
    grid.  This heat exchanger is defined to be on the primary side of the network
    (i.e. as a part of the network itself).

    Inherits from EnergyConversionSystem.

    Parameters
    ----------
    network_id : string
        Unique identifier of network object.
    network_node_id : string
        Unique identifier of network node to which the energy conversion system is
        connected.
    primary_heat_supplier : string
        ***Description missing.***

    """

    _energy_system = models.OneToOneField(
        EnergyConversionSystem,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="heat_exchanger_obj",
    )
    network_id = models.CharField(
        max_length=1000, blank=True, null=True, db_column="networkid"
    )
    network_node_id = models.CharField(
        max_length=1000, blank=True, null=True, db_column="networknodeid"
    )
    primary_heat_supplier = models.CharField(
        max_length=1000, blank=True, null=True, db_column="primaryheatsupplier"
    )

    class Meta:
        """Metaclass of HeatExchanger."""

        managed = False
        db_table = "ng_heatexchanger"
