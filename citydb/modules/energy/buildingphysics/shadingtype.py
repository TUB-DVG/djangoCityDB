"""This module contains the class ShadingType from EnergyADE."""

from django.contrib.gis.db import models
from citydb.modules.energy.materials.transmittance import Transmittance


class ShadingType(models.Model):
    """ORM class for shading_type table from EnergyADE.

    Shading system of the considered opening.

    Parameters
    ----------
    maximum_cover_ratio : Decimal
        Maximum fraction of the related opening which can be covered with the shading
        device, must be between 0 and 1.
    maximum_cover_ratio_uom : string
        Defines the unit of measurement of maximum_cover_ratio.
    name : string
        Name of the Shading system.
    transmittance : Transmittance
        Foreign key to the corresponding Transmittance instance.

    """

    maximum_cover_ratio = models.DecimalField(
        db_column="maximumcoverratio",
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    maximum_cover_ratio_uom = models.CharField(
        db_column="maximumcoverratio_uom", max_length=1000, blank=True, null=True
    )
    name = models.CharField(max_length=1000, blank=True, null=True)
    transmittance = models.ForeignKey(
        Transmittance, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        """Metaclass of ShadingType."""

        managed = False
        db_table = "ng_shadingtype"
