"""This module contains the class BuildingUnit from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.energy.occupants.usagezone import UsageZone
from citydb.modules.bldg.address import Address


class BuildingUnit(CityObject):
    """ORM class for building_unit table from EnergyADE.

    A building unit is a part of a usage zone, such as dwelling or workplace, which is
    related to a single occupant entity.

    Parameters:
    -----------
    number_of_rooms : integer
        Number of separated rooms other than a circulation space in the building unit.
    owner_name : string
        Name of the owner.
    ownership_type : string
        Type of organisations, associations, businesses etc. that owns the building
        (e.g. individual, public authority, property management company, non-profit
        organisation etc.).
    ownership_type_codespace : string
        Describes the used methodology for ownership_type.
    usage_zone : UsageZone
        Foreign key to the corresponding UsageZone instance.
    address : Address
        Reference to the adress this building unit belongs to.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="buildingunit_obj",
    )
    number_of_rooms = models.IntegerField(
        blank=True, null=True, db_column="numberofrooms"
    )
    owner_name = models.CharField(
        max_length=1000, blank=True, null=True, db_column="ownername"
    )
    ownership_type = models.CharField(
        max_length=1000, blank=True, null=True, db_column="ownershiptype"
    )
    ownership_type_codespace = models.CharField(
        max_length=1000, blank=True, null=True, db_column="ownershiptype_codespace"
    )
    usage_zone = models.ForeignKey(
        UsageZone,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="usagezone_contains_id",
    )
    address = models.ManyToManyField(Address, through="BuildingUnitToAddress")

    class Meta:
        """Metaclass of BuildingUnit."""

        managed = False
        db_table = "ng_buildingunit"


class BuildingUnitToAddress(models.Model):
    """A mapping table to manage the relations of addresses and building units.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    address = models.ForeignKey(Address, models.DO_NOTHING, primary_key=True)
    building_unit = models.ForeignKey(
        BuildingUnit, models.DO_NOTHING, db_column="buildingunit"
    )

    class Meta:
        """Metaclass of BuildingUnitToAddress."""

        managed = False
        auto_created = True
        db_table = "ng_buildingu_to_address"
        unique_together = (("address", "building_unit"),)
