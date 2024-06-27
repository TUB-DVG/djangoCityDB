"""This module contains the class Facilities and the derived class DHWFacilities from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.energy.occupants.buildingunit import BuildingUnit
from citydb.modules.energy.occupants.usagezone import UsageZone
from citydb.modules.core.objectclass import ObjectClass
from citydb.modules.energy.core.heatexchange import HeatExchangeType
from citydb.modules.energy.schedule.schedule import TimeSeriesSchedule


class Facilities(CityObject):
    """ORM class for facilities table from EnergyADE.

    Facilities and Appliances inside the usage zone or building unit, which consume
    and dissipate energy.

    Parameters:
    -----------
    building_unit_equipped_with : BuildingUnit
        Foreign key to the corresponding BuildingUnit instance.
    electrical_power : float [W]
        Nominal electrical power of the electrical appliance.
    electrical_power_uom : string
        Defines the unit of measurement of electrical_power, should always be [W].
    heat_dissipation : HeatExchangeType
        Heat energy per year (in W) dissipated by the facilities, in "nominal
        conditions", when the facilities are fully operating. The constant totalValue
        of heatDissipation is weighted by the operationSchedule, to obtain the heat
        dissipation temporal variation.
    objectclass_facilities : ObjectClass
        Foreign key to the corresponding ObjectClass instance.
    operation_schedule : TimeSeriesSchedule
        Operational schedule of the facilities.
    usage_zone_equipped_with : UsageZone
        Foreign key to the corresponding UsageZone instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="facilities_obj",
    )
    building_unit_equipped_with = models.ForeignKey(
        BuildingUnit,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="buildingunit_equippedwith_id",
    )
    electrical_power = models.FloatField(
        blank=True, null=True, db_column="electricalpower"
    )
    electrical_power_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="electricalpower_uom"
    )
    heat_dissipation = models.ForeignKey(
        HeatExchangeType,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="heatdissipation_id",
    )
    objectclass_facilities = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )
    operation_schedule = models.ForeignKey(
        TimeSeriesSchedule,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="operationschedule_id",
        related_name="facilites",
    )
    usage_zone_equipped_with = models.ForeignKey(
        UsageZone,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="usagezone_equippedwith_id",
        related_name="facilities",
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for thematic surface.

        Since 3D CityDB 4.0.0 every Facilities has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        super(Facilities, self).__init__(*args, **kwargs)
        try:
            self.objectclass_facilities = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate Facilities without passing "
                "an ObjectClass"
            )

    class Meta:
        """Metaclass of Facilities."""

        managed = False
        db_table = "ng_facilities"


class DHWFacilities(Facilities):
    """ORM class for dhw_facilities table from EnergyADE.

    Facilities for domestic hot water usage.

    Parameters:
    -----------
    number_of_baths : integer
        Number of baths in a given building unit/zone.
    number_of_showers : integer
        Number of showers in a given building unit/zone.
    number_of_wash_basins : integer
        Number of wash basin in a given building unit/zone.
    water_storage_volume : float [m³]
        Volume of water storage in a given building unit/zone.
    water_storage_volume_uom : string
        Defines the unit of measurement of water_storage_volume, should always be [m³].

    """

    _abst_facilities = models.OneToOneField(
        Facilities,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="DHW_abstract",
    )
    number_of_baths = models.IntegerField(
        blank=True, null=True, db_column="numberofbaths"
    )
    number_of_showers = models.IntegerField(
        blank=True, null=True, db_column="numberofshowers"
    )
    number_of_wash_basins = models.IntegerField(
        blank=True, null=True, db_column="numberofwashbasins"
    )
    water_storage_volume = models.FloatField(
        blank=True, null=True, db_column="waterstoragevolume"
    )
    water_storage_volume_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="waterstoragevolume_uom"
    )

    class Meta:
        """Metaclass of DHWFacilities."""

        managed = False
        db_table = "ng_dhwfacilities"
