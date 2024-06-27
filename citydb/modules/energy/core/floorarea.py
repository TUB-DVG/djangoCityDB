"""This module contains the class FloorArea from EnergyADE."""

from citydb.modules.energy.core.energybuilding import EnergyBuilding
from django.contrib.gis.db import models
from citydb.modules.energy.buildingphysics.thermalzone import ThermalZone
from citydb.modules.energy.occupants.buildingunit import BuildingUnit
from citydb.modules.energy.occupants.usagezone import UsageZone
from django.db import connection


def sequence_id():
    """Get next value of floor_area sequence."""

    with connection.cursor() as cursor:

        cursor.execute("""SELECT nextval('ng_floorarea_seq')""")
        return cursor.fetchone()[0]


class FloorArea(models.Model):
    """ORM class for floor_area table from EnergyADE.

    Floor area. ***More detailed description missing***

    Parameters
    ----------
    building : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.
    building_unit : BuildingUnit
        Foreign key to the corresponding BuildingUnit instance.
    thermal_zone : ThermalZone
        Foreign key to the corresponding ThermalZone instance.
    usage_zone : UsageZone
        Foreign key to the corresponding UsageZone instance.
    area_type_choices : tuple
        Type Choices for type.
    type : string
        Categorization of a method to calculate the floor area.
    value : float [m²]
        Floor area value.
    value_uom : string
        Defines the unit of measurement of value, should always be [m²].

    """

    _floor_area = models.IntegerField(db_column="id", default=sequence_id)
    building = models.ForeignKey(
        EnergyBuilding,
        models.CASCADE,
        db_column="building_floorarea_id",
        blank=True,
        null=True,
        related_name="floor_area_bldg",
    )
    building_unit = models.ForeignKey(
        BuildingUnit,
        models.CASCADE,
        db_column="buildingunit_floorarea_id",
        blank=True,
        null=True,
        related_name="floor_area_bldg_unit",
    )
    thermal_zone = models.ForeignKey(
        ThermalZone,
        models.CASCADE,
        db_column="thermalzone_floorarea_id",
        blank=True,
        null=True,
        related_name="floor_area_tz",
    )
    usage_zone = models.ForeignKey(
        UsageZone,
        models.CASCADE,
        db_column="usagezone_floorarea_id",
        blank=True,
        null=True,
        related_name="floor_area_uz",
    )
    area_type_choices = (
        ("netFloorArea", "netFloorArea"),
        ("grossFloorArea", "grossFloorArea"),
        ("energyReferenceArea", "energyReferenceArea"),
    )
    type = models.CharField(
        max_length=1000, blank=True, null=True, choices=area_type_choices
    )
    value = models.FloatField(blank=True, null=True)
    value_uom = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        """Metaclass of FloorArea."""

        managed = False
        auto_created = True
        db_table = "ng_floorarea"
