"""This module contains the class Emissivity from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.energy.materials.opticalproperties import OpticalProperties


class Emissivity(models.Model):
    """ORM class for emissivity table from EnergyADE.

    Percentaged infra-red emissivity.

    Parameters:
    -----------
    fraction : Decimal
        Fraction of energy emittance, must be between 0 and 1.
    fraction_uom : string
        Defines the unit of measurement of fraction.
    side_type_choices : tuple
        Type choices for surface.
    surface : string
        Considered surface of the construction.

    """

    _optical_properties = models.ForeignKey(
        OpticalProperties,
        models.CASCADE,
        db_column="opticalpropert_emissivity",
        blank=True,
        null=True,
        related_name="emissivity",
    )
    fraction = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    fraction_uom = models.CharField(max_length=1000, blank=True, null=True)
    side_type_choices = (("inside", "inside"), ("outside", "outside"))
    surface = models.CharField(
        max_length=1000, blank=True, null=True, choices=side_type_choices
    )

    class Meta:
        """Metaclass of Emissivity."""

        managed = False
        db_table = "ng_emissivity"
