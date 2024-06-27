"""This module contains the class OpticalProperties from EnergyADE."""
from django.contrib.gis.db import models


class OpticalProperties(models.Model):
    """ORM class for optical_properties table from EnergyADE.

    Parameters:
    -----------
    glazing_ratio : Decimal
        Ratio of the glazing surface over the total construction surface, must be
        between 0 and 1.
    glazing_ratio_uom : string
        Defines the unit of measurement of glazing_ratio.

    """

    glazing_ratio = models.DecimalField(
        db_column="glazingratio",
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    glazing_ratio_uom = models.CharField(
        db_column="glazingratio_uom", max_length=1000, blank=True, null=True
    )

    class Meta:
        """Metaclass of OpticalProperties."""

        managed = False
        db_table = "ng_opticalproperties"
