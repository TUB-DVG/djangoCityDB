"""This module contains the class HeightAboveGround from EnergyADE."""

from citydb.modules.energy.core.energybuilding import EnergyBuilding
from django.contrib.gis.db import models
from django.db import connection


def sequence_id():
    """Get next value of height_above_ground sequence."""
    with connection.cursor() as cursor:
        cursor.execute("""SELECT nextval('ng_heightabovegroun_seq')""")
        return cursor.fetchone()[0]


class HeightAboveGround(models.Model):
    """ORM class for height_above_ground table from EnergyADE.

    Different kinds of building height above general ground level. The general ground
    level lies anywhere between the lowest and the highest ground points of the
    construction.

    Parameters
    ----------
    building : EnergyBuilding
        Foreign key relationship to the building.
    height_type_choices : tuple
        Type Choices for height_reference.
    height_reference : string
        Specification of the building height reference, which is measured relative to
        general ground level.
    value : float [m]
        Height value.
    value_uom : string
        Defines the unit of measurement of value, should always be [m].

    """

    _height_above_ground = models.IntegerField(db_column="id", default=sequence_id)
    building = models.ForeignKey(
        EnergyBuilding,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="building_heightabovegroun_id",
        related_name="height_above_ground_bldg",
    )
    height_type_choices = (
        ("bottomOfConstruction", "bottomOfConstruction"),
        ("entrancePoint", "entrancePoint"),
        ("generalEave", "generalEave"),
        ("generalRoof", "generalRoof"),
        ("generalRoofEdge", "generalRoofEdge"),
        ("highestEave", "highestEave"),
        ("highestPoint", "highestPoint"),
        ("highestRoofEdge", "highestRoofEdge"),
        ("lowestEave", "lowestEave"),
        ("lowestFloorAboveGround", "lowestFloorAboveGround"),
        ("lowestRoofEdge", "lowestRoofEdge"),
        ("topOfConstruction", "topOfConstruction"),
        ("topThermalBoundary", "topThermalBoundary"),
        ("bottomThermalBoundary", "bottomThermalBoundary"),
    )
    height_reference = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        choices=height_type_choices,
        db_column="heightreference",
    )
    value = models.FloatField(blank=True, null=True)
    value_uom = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        """Metaclass of HeightAboveGround."""

        managed = False
        auto_created = True
        db_table = "ng_heightaboveground"
