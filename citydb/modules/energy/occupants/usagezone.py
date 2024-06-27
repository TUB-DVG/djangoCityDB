"""This module contains the class UsageZone from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.energy.core.energybuilding import EnergyBuilding
from citydb.modules.energy.buildingphysics.thermalzone import ThermalZone
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from citydb.modules.energy.core.heatexchange import HeatExchangeType
from citydb.modules.energy.schedule.schedule import TimeSeriesSchedule


class UsageZone(CityObject):
    """ORM class for usage_zone table from EnergyADE.

    A usage zone is a zone of a building with homogeneous usage type.

    Parameters:
    -----------
    average_internal_gains : HeatExchangeType
        Aggregated average heat energy per year (in W) dissipated by the occupants and
        facilities in a usage zone over the whole year (positive for heat source,
        negative for heat sink/cool source).
    building : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.
    cooling_schedule : TimeSeriesSchedule
        Temperature schedule [°C] of the active cooling inside the usage zone.
    heating_schedule : TimeSeriesSchedule
        Temperature schedule [°C] of the active heating inside the usage zone.
    thermal_zone : ThermalZone
        Foreign key to the corresponding BuildingUnit instance.
    usage_zone_type : string
        Usage class of the zone.
    usage_zone_type_codespace : string
        Describes the used methodology for usage_zone_type.
    used_floors : string
        List of the number of floors part of the usage zone (0 = ground level).
    ventilation_schedule : TimeSeriesSchedule
        Air change rate [1/h] schedule of the ventilation system inside the usage zone.
    volume_geometry : SurfaceGeometry
        Geometric representation of the UsageZone volume.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="usagezone_obj",
    )
    # average_internal_gains = models.ForeignKey(
    #     HeatExchangeType,
    #     models.DO_NOTHING,
    #     blank=True,
    #     null=True,
    #     db_column="averageinternalgains_id",
    # )
    building = models.ForeignKey(
        EnergyBuilding,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="building_usagezone_id",
    )
    cooling_schedule = models.ForeignKey(
        TimeSeriesSchedule,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="coolingschedule_id",
        related_name="usagezone_cooling",
    )
    heating_schedule = models.ForeignKey(
        TimeSeriesSchedule,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="heatingschedule_id",
        related_name="usagezone_heating",
    )
    thermal_zone = models.ForeignKey(
        ThermalZone,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="thermalzone_contains_id",
        related_name="usage_zone",
    )
    usage_zone_type = models.CharField(
        max_length=1000, blank=True, null=True, db_column="usagezonetype"
    )
    usage_zone_type_codespace = models.CharField(
        max_length=1000, blank=True, null=True, db_column="usagezonetype_codespace"
    )
    # used_floors = models.CharField(
    #     max_length=1000, blank=True, null=True, db_column="usedfloors"
    # )
    ventilation_schedule = models.ForeignKey(
        TimeSeriesSchedule,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="ventilationschedule_id",
        related_name="usagezone_vent",
    )
    # volume_geometry = models.ForeignKey(
    #     SurfaceGeometry,
    #     models.CASCADE,
    #     blank=True,
    #     null=True,
    #     db_column="volumegeometry_id",
    # )

    class Meta:
        """Metaclass of UsageZone."""

        managed = False
        db_table = "ng_usagezone"

    def __init__(self, *args, **kwargs):
        """Constructor of Usagezone.

        This constructor instantiates the parent CityObject

        """

        super(UsageZone, self).__init__(*args, **kwargs)
        # breakpoint()
        try:
            self.objectclass_series = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate TimeSeries without passing "
                "an ObjectClass"
            )

    @property
    def floor_area(self):
        """Return floor_area."""
        value = self.floor_area_uz.get(type="energyReferenceArea").value
        return value

    @floor_area.setter
    def floor_area(self, value):
        """Set floor_area."""
        from citydb.models import FloorArea

        FloorArea(
            usage_zone=self, type="energyReferenceArea", value=value, value_uom="sqm"
        ).save()
