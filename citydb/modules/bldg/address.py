"""This module contains the classes Address and AddressToBuilding from 3DCityDB."""


from django.contrib.gis.db import models
from citydb.modules.bldg.building import Building


class Address(models.Model):
    """ORM class for address table from 3DCityDB.

    This class enables linking address information to a given Building or
    Building object.

    Parameters
    ----------
    building : Building
        Reference to the building this address belongs to.
    gmlid : string
        Unique identifier of CityGML object.
    gmlid_codespace : string
        As it cannot be guarenteed that the gmlid is unique over different
        projects you can specify the codespace.
    street : string
        Name of the street.
    house_number : string
        House number of the building.
    po_box : string
        Post box.
    zip_code : string
        This address' zip code.
    city : string
        Name of the city.
    state : string
        Name of the state.
    country : string
        Name of the country.
    multi_point : MultiPoint
        A reference geometry for this address.
    xal_source : string
        A reference to the source of the address type.

    """

    building = models.ManyToManyField(
        Building, blank=True, through="AddressToBuilding", related_name="addresses"
    )
    gmlid = models.CharField(max_length=256, blank=True, null=True)
    gmlid_codespace = models.CharField(max_length=1000, blank=True, null=True)
    street = models.CharField(max_length=1000, blank=True, null=True)
    house_number = models.CharField(max_length=256, blank=True, null=True)
    po_box = models.CharField(max_length=256, blank=True, null=True)
    zip_code = models.CharField(max_length=256, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=256, blank=True, null=True)
    multi_point = models.MultiPointField(dim=3, srid=25832, blank=True, null=True)
    xal_source = models.TextField(blank=True, null=True)

    def __str__(self):
        """Return building id, street and house number."""
        return "Address {} ({} {})".format(self.id, self.street, self.house_number)

    class Meta:
        """Metaclass of Address."""

        managed = False
        db_table = "address"


class AddressToBuilding(models.Model):
    """A mapping table to manage the relations of addresses and buildings.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    building = models.OneToOneField(Building, models.DO_NOTHING, primary_key=True)
    address = models.ForeignKey(Address, models.DO_NOTHING)

    class Meta:
        """Metaclass of AddressToBuilding."""

        managed = False
        auto_created = True
        db_table = "address_to_building"
        unique_together = (("building", "address"),)
