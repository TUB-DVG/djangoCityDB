"""This module contains the class Reflectance from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.energy.materials.opticalproperties import OpticalProperties


class Reflectance(models.Model):
    """ORM class for reflectance table from EnergyADE.

    Effectiveness of a material surface in reflecting an incident radiant flux of a
    given wavelength range.

    Parameters:
    -----------
    fraction : Decimal
        Fraction of energy reflectance, must be between 0 and 1.
    fraction_uom : string
        Defines the unit of measurement of fraction.
    side_type_choices : tuple
        Type choices for surface.
    surface : string
        Considered surface of the construction.
    wave_type_choices : tuple
        Type choices for wavelength.
    wavelength_range : string
        Wavelength range of the incident radiant flux, for which the absorptance ratio
        is defined.

    """

    _optical_properties = models.ForeignKey(
        OpticalProperties,
        models.CASCADE,
        db_column="opticalproper_reflectance",
        blank=True,
        null=True,
        related_name="reflectance",
    )
    fraction = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    fraction_uom = models.CharField(max_length=1000, blank=True, null=True)
    side_type_choices = (("inside", "inside"), ("outside", "outside"))
    surface = models.CharField(
        max_length=1000, blank=True, null=True, choices=side_type_choices
    )
    wave_type_choices = (
        ("solar", "solar"),
        ("infrared", "infrared"),
        ("visible", "visible"),
        ("total", "total"),
    )
    wavelength_range = models.CharField(
        db_column="wavelengthrange",
        max_length=1000,
        blank=True,
        null=True,
        choices=wave_type_choices,
    )

    class Meta:
        """Metaclass of Reflectance."""

        managed = False
        db_table = "ng_reflectance"
