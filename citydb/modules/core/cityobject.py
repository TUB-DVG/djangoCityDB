"""This module contains the class CityObject from 3DCityDB."""

from django.contrib.gis.db import models
from citydb.modules.core.objectclass import ObjectClass


class CityObject(models.Model):
    """ORM class for city_object table from 3DCityDB.

    A CityObject is the base class for many other CityGML classes (like
    buildings). These classes are connected by a OneToOneField, so a CityObject
    needs to be instantiated to insert a building for example. Many foreign
    keys point to a CityObject instead of the class itself, thus the CityObject
    ORM class provides access to many information. CityObject information is
    accessible through the `id` of the related instance.

    Parameters
    ----------
    objectclass : ObjectClass
        Foreign key to objectclass identifier of this object.
    gmlid : string
        Unique identifier of CityGML object.
    gmlid_codespace : string
        As it cannot be guarenteed that the gmlid is unique over different
        projects you can specify the codespace.
    name : string
        Each object has a unique name, which is a human readable identifier.
    name_codespace : string
        As it cannot be guarenteed that the name is unique over different
        projects you can specify the codespace.
    description : string
        A string that gives additional information about the object.
    envelope : Polygon
        The Envelope is realized as rectangular geometry using five points,
        that join the minimum and maximum x, y and z coordinates of the
        envelope and define it (usage not recommended).
    creation_date : datetime
        Date of entry into the database (do not mix with e.g. year_of_construction of
        building).
    termination_date : datetime
        Date of termination of the city object.
    relative_to_terrain : string
        Attribute denoting a city object’s location with respect to the
        surrounding terrain.
    relative_to_water : string
        Attribute denoting a city object’s location with respect to the
        surrounding water.
    last_modification_date : datetime
        Date of modification.
    updating_person : string
        Name of last updating person.
    reason_for_update : string
        Give a reason for updates.
    lineage : string
        Source of data that has been inserted/updated.
    xml_source : string
        File name of the XML_Source, if imported by 3DCityImporter.

    """

    objectclass = models.ForeignKey(ObjectClass, on_delete=models.CASCADE)
    gmlid = models.CharField(max_length=256, blank=True, null=True)
    gmlid_codespace = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    name_codespace = models.CharField(max_length=4000, blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    envelope = models.PolygonField(dim=3, srid=25832, blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    termination_date = models.DateTimeField(blank=True, null=True)
    relative_to_terrain = models.CharField(max_length=256, blank=True, null=True)
    relative_to_water = models.CharField(max_length=256, blank=True, null=True)
    last_modification_date = models.DateTimeField(blank=True, null=True)
    updating_person = models.CharField(max_length=256, blank=True, null=True)
    reason_for_update = models.CharField(max_length=4000, blank=True, null=True)
    lineage = models.CharField(max_length=256, blank=True, null=True)
    xml_source = models.TextField(blank=True, null=True)

    class Meta:
        """Metaclass of CityObject."""

        managed = False
        abstract = False
        db_table = "cityobject"

# class GenericCityObject(models.Model):
#     """ORM class for the GenericCityObject table from 3DCityDB.

#     A definition of the class can be checked out here:
#     https://3dcitydb-docs.readthedocs.io/en/release-v4.1/3dcitydb/uml/thematic-model/generic-city-object.html
#     """
class NgCityObject(models.Model):
    """ORM class for the ng_cityobject table from 3DCityDB.

    """
    id = models.OneToOneField(
        CityObject,
        db_column="id",
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        managed = False
        db_table = "ng_cityobject"