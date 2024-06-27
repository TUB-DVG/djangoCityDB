"""This module contains the class SystemOperation from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.energy.energysystems.energysystem import EnergyConversionSystem
from citydb.modules.energy.schedule.schedule import TimeSeriesSchedule
from citydb.modules.core.cityobject import CityObject


class SystemOperation(CityObject):
    """ORM class for system_operation table from EnergyADE.

    Operation mode details of the operation of the energy conversion system for a
    specific end-use and operation time.

    Parameters
    ----------
    end_use_choices : tuple
        Type choices for end_use.
    end_use : string
        Category of end use related to an energy use.
    energy_conversion_system : EnergyConversionSystem
        Foreign key to the corresponding EnergyConversionSystem instance.
    operation_time : TimeSeriesSchedule
        The operation time can be specified by an irregular time series.
    yearly_global_efficiency : float
        ***Description missing.****

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="_system_operation_obj",
    )
    end_use_choices = (
        ("domesticHotWater", "domesticHotWater"),
        ("electricalAppliances", "electricalAppliances"),
        ("lighting", "lighting"),
        ("otherOrCombinationElectrical", "otherOrCombinationElectrical"),
        ("otherOrCombinationHeating", "otherOrCombinationHeating"),
        ("otherOrCombinationCooling", "otherOrCombinationCooling"),
        ("spaceCooling", "spaceCooling"),
        ("spaceHeating", "spaceHeating"),
        ("ventilation", "ventilation"),
        ("ventilationHeating", "ventilationHeating"),
        ("ventilationCooling", "ventilationCooling"),
        ("process", "process"),
    )
    end_use = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        db_column="enduse",
        choices=end_use_choices,
    )
    energy_conversion_system = models.ForeignKey(
        EnergyConversionSystem,
        models.CASCADE,
        db_column="energyconversionsyste_has_id",
        blank=True,
        null=True,
        related_name="system_operation",
    )
    operation_time = models.ForeignKey(
        TimeSeriesSchedule,
        models.CASCADE,
        db_column="operationtime_id",
        blank=True,
        null=True,
    )
    yearly_global_efficiency = models.FloatField(
        blank=True, null=True, db_column="yearlyglobalefficiency"
    )

    class Meta:
        """Metaclass of SystemOperation."""

        managed = False
        db_table = "ng_systemoperation"
