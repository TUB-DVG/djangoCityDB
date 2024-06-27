"""This module contains the class VolumeType from EnergyADE."""

from citydb.modules.energy.core.energybuilding import EnergyBuilding
from citydb.modules.energy.buildingphysics.thermalzone import ThermalZone
from django.contrib.gis.db import models
from django.db import connection


def sequence_id():
    """Get next value of volume_type sequence."""
    with connection.cursor() as cursor:
        cursor.execute("""SELECT nextval('ng_volumetype_seq')""")
        return cursor.fetchone()[0]


class VolumeType(models.Model):
    """ORM class for volume_type table from EnergyADE.

    Volume of e.g. a ThermalZone or UsageZone.

    Parameters
    ----------
    building : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.
    thermal_zone : ThermalZone
        Foreign key to the corresponding ThermalZone instance.
    vol_type_choices : tuple
        Type choices for type.
    type : string
        Categorization of a method to calculate the volume.
    value : float [m³]
        Volume value.
    value_uom : string
        Defines the unit of measurement of value, should always be [m³].

    """

    _id_vol = models.IntegerField(db_column="id", default=sequence_id)
    building = models.ForeignKey(
        EnergyBuilding,
        models.CASCADE,
        db_column="building_volume_id",
        blank=True,
        null=True,
        related_name="volume_bldg",
    )
    thermal_zone = models.ForeignKey(
        ThermalZone,
        models.CASCADE,
        db_column="thermalzone_volume_id",
        blank=True,
        null=True,
        related_name="volume_tz",
    )
    vol_type_choices = (
        ("netVolume", "netVolume"),
        ("grossVolume", "grossVolume"),
        ("energyReferenceVolume", "energyReferenceVolume"),
    )
    type = models.CharField(
        max_length=1000, blank=True, null=True, choices=vol_type_choices
    )
    value = models.FloatField(blank=True, null=True)
    value_uom = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        """Metaclass of VolumeType."""

        managed = False
        auto_created = True
        db_table = "ng_volumetype"
