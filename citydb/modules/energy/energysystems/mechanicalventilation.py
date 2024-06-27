"""This module contains the class MechanicalVentilation from EnergyADE."""
from citydb.modules.energy.energysystems.energysystem import EnergyConversionSystem
from django.contrib.gis.db import models


class MechanicalVentilation(EnergyConversionSystem):
    """ORM class for mechanical_ventilation table from EnergyADE.

    Class for mechanical ventilation in the building (likely to be extended for
    projects.)

    Inherits from _EnergySystem

    Parameters
    ----------
    recuperation_factor : float
        Factor of recuperation of the heat recovery.
    recuperation_factor_uom : string
        Defines the unit of measurement of recuperation_factor.

    """

    _energy_system = models.OneToOneField(
        EnergyConversionSystem,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="mechanical_ventilation_obj",
    )
    _has_heat_recovery = models.IntegerField(
        db_column="hasheatrecovery", blank=True, null=True
    )
    recuperation_factor = models.FloatField(
        db_column="recuperationfactor", blank=True, null=True
    )
    recuperation_factor_uom = models.CharField(
        db_column="recuperationfactor_uom", max_length=1000, blank=True, null=True
    )
    _humidification = models.IntegerField(
        db_column="humidification", blank=True, null=True
    )
    _dehumidification = models.IntegerField(
        db_column="dehumidification", blank=True, null=True
    )

    class Meta:
        """Metaclass of MechanicalVentilation."""

        managed = False
        db_table = "ng_mechanicalventilatio"

    @property
    def has_heat_recovery(self):
        """Return has_heat_recovery."""
        translate = {0: False, 1: True}
        value = translate[self._has_heat_recovery]
        return value

    @has_heat_recovery.setter
    def has_heat_recovery(self, value):
        """Set has_heat_recovery."""
        translate = {False: 0, True: 1}
        self._has_heat_recovery = translate[value]

    @property
    def humidification(self):
        """Return humidification."""
        translate = {0: False, 1: True}
        value = translate[self._humidification]
        return value

    @humidification.setter
    def humidification(self, value):
        """Set humidification."""
        translate = {False: 0, True: 1}
        self._humidification = translate[value]

    @property
    def dehumidification(self):
        """Return dehumidification."""
        translate = {0: False, 1: True}
        value = translate[self._dehumidification]
        return value

    @dehumidification.setter
    def dehumidification(self, value):
        """Set dehumidification."""
        translate = {False: 0, True: 1}
        self._dehumidification = translate[value]
