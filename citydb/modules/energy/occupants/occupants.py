"""This module contains the class Occupants from EnergyADE."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.energy.occupants.buildingunit import BuildingUnit
from citydb.modules.energy.occupants.usagezone import UsageZone
from citydb.modules.energy.core.heatexchange import HeatExchangeType
from citydb.modules.energy.schedule.schedule import TimeSeriesSchedule


class Occupants(CityObject):
    """ORM class for occupants table from EnergyADE.

    Occupants is an aggregated group of occupants of a usage zone or building unit,
    which can be residents, workers, visitors etc.

    Parameters:
    -----------
    building_unit_occupied_by : BuildingUnit
        Foreign key to the corresponding BuildingUnit instance.
    heat_dissipation : HeatExchangeType
        Heat energy per year (in W) dissipated by the occupants in "nominal
        conditions", when all occupants are present. The constant totalValue of
        heatDissipation is weighted by the occupancyRate, to obtain the heat
        dissipation temporal variation.
    number_of_occupants : integer
        Number of occupants of the considered zone/building unit.
    occupancy_rate : TimeSeriesSchedule
        Schedule of room/zone occupancy (0 while empty, 1 while occupied with the
        specified full number of occupant, between 0 and 1 during partial occupancy).
    occupant_type : string
        Type of occupants of a premises.
    occupant_type_codespace : string
        Describes the used methodology for occupant_type.
    usage_zone_occupied_by : UsageZone
        Foreign key to the corresponding UsageZone instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="occupants_obj",
    )
    # building_unit_occupied_by = models.ForeignKey(
    #     BuildingUnit,
    #     models.DO_NOTHING,
    #     blank=True,
    #     null=True,
    #     db_column="buildingunit_occupiedby_id",
    # )
    heat_dissipation = models.ForeignKey(
        HeatExchangeType,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="heatdissipation_id",
    )
    number_of_occupants = models.IntegerField(
        blank=True, null=True, db_column="numberofoccupants"
    )
    occupancy_rate = models.ForeignKey(
        TimeSeriesSchedule,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="occupancyrate_id",
        related_name="occupancy_rate",
    )
    # occupant_type = models.CharField(
    #     max_length=1000, blank=True, null=True, db_column="occupanttype"
    # )
    # occupant_type_codespace = models.CharField(
    #     max_length=1000, blank=True, null=True, db_column="occupanttype_codespace"
    # )
    usage_zone_occupied_by = models.ForeignKey(
        UsageZone,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="usagezone_occupiedby_id",
        related_name="occupants",
    )

    class Meta:
        """Metaclass of Occupants."""

        managed = False
        db_table = "ng_occupants"
