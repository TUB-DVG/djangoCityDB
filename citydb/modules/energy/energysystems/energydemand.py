"""This module contains the class EnergyDemand from EnergyADE."""

from citydb.modules.core.cityobject import (
    CityObject,
    NgCityObject,
    ObjectClass,
)
from django.contrib.gis.db import models
from citydb.modules.energy.timeseries.timeseries import TimeSeries


class EnergyDemand(CityObject):
    """Abstract ORM class for energy demand from EnergyADE.

    Documentation is missing.

    demands means: all buildings that are provided by one HEEX
    is_demanded_by: is the heat exchanger / ecs that
    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="energy_demand_obj",
    )
    # demands = models.ManyToManyField(
    #     CityObject, through="EnergyDemandToCityObject", related_name="energy_demand"
    # )
    cityObjectDemandsID = models.OneToOneField(
        NgCityObject,
        db_column="cityobject_demands_id",
        on_delete=models.CASCADE,
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
    energy_amount = models.ForeignKey(
        TimeSeries,
        db_column="energyamount_id",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="time_series_demand",
    )
    energy_carrier_type = models.CharField(
        max_length=1000, blank=True, null=True, db_column="energycarriertype"
    )
    energy_carrier_type_codespace = models.CharField(
        max_length=1000, blank=True, null=True, db_column="energycarriertype_codespace"
    )
    maximum_load = models.FloatField(db_column="maximumload", blank=True, null=True)
    maximum_load_uom = models.FloatField(
        db_column="maximumload_uom", blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "ng_energydemand"

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for TimeSeries.

        Since 3D CityDB 4.0.0 every TimeSeries has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        
        super(EnergyDemand, self).__init__(*args, **kwargs)
        # breakpoint()
        try:
            self.objectclass_series = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate TimeSeries without passing "
                "an ObjectClass"
            )

# class EnergyDemandToCityObject(models.Model):
#     city_object = models.ForeignKey(
#         CityObject, models.DO_NOTHING, primary_key=True, db_column="cityobject_id"
#     )
#     energy_demand = models.ForeignKey(
#         EnergyDemand, models.DO_NOTHING, db_column="energydemand_id"
#     )

#     class Meta:
#         managed = False
#         auto_created = True
#         db_table = "ng_energydem_to_cityobjec"
#         unique_together = (("city_object", "energy_demand"),)
