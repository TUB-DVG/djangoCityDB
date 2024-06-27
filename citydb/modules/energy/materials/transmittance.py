"""This module contains the class Transmittance from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.energy.materials.opticalproperties import OpticalProperties


class Transmittance(models.Model):
    """ORM class for transmittance table from EnergyADE.

    Percentaged energy transmittance in different wavelength ranges. Effectiveness of a
    construction in transmitting an incident radiant flux of a given wavelength range.

    Parameters:
    -----------
    fraction : Decimal
        Fraction of energy reflectance, must be between 0 and 1.
    fraction_uom : string
        Defines the unit of measurement of fraction.
    wave_type_choices : tuple
        Type choices for wavelength_range.
    wavelength_range : string
        Wavelength range of the incident radiant flux, for which the absorptance ratio
        is defined.

    """

    _optical_properties = models.ForeignKey(
        OpticalProperties,
        models.CASCADE,
        db_column="opticalprope_transmittanc",
        blank=True,
        null=True,
        related_name="transmittance",
    )
    fraction = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    fraction_uom = models.CharField(max_length=1000, blank=True, null=True)
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
        """Metaclass of Transmittance."""

        managed = False
        db_table = "ng_transmittance"
