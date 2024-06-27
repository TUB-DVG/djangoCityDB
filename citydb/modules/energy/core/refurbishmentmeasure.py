"""This module contains the class RefurbishmentMeasure from EnergyADE."""

from citydb.modules.energy.core.energybuilding import EnergyBuilding
from citydb.modules.energy.buildingphysics.thermalboundary import ThermalBoundary
from django.contrib.gis.db import models


class RefurbishmentMeasure(models.Model):
    """ORM class for refurbishment_measure table from EnergyADE.

    Information on a refurbishment measure.

    Parameters
    ----------
    building_refurbishment : EnergyBuilding
        Foreign key to the the corresponding EnergyBuilding instance.
    date : DateOfEvent
        Date of the refurbishment measure.
    description : string
        Description of refurbishment measure.
    level_field : string
        Level of refurbishment.
    level_codespace : string
        Describes the used methodology for level_field.
    thermalbound_refurbishment : ThermalBoundary
        Foreign key to the the corresponding ThermalBoundary instance.

    """

    building_refurbishment = models.ForeignKey(
        EnergyBuilding,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="refurbishment_measure_bld",
    )
    # date = models.ForeignKey(
    #     DateOfEvent,
    #     models.DO_NOTHING,
    #     blank=True,
    #     null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    # Field renamed because it ended with '_'.
    level_field = models.CharField(
        db_column="level_", max_length=1000, blank=True, null=True
    )
    level_codespace = models.CharField(max_length=1000, blank=True, null=True)
    thermalbound_refurbishment = models.ForeignKey(
        ThermalBoundary,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="refurbishment_measure_tb",
    )

    class Meta:
        """Metaclass of EnergyPerformanceCertificate."""

        managed = False

        db_table = "ng_refurbishmentmeasure"
