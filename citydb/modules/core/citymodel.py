"""This module contains the classes CityModel and CityObjectMember from 3DCityDB."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class CityModel(models.Model):
    """ORM class for city_model table from 3DCityDB.

    ***Description missing; Parameter descripition is derived from parameters of class
    CityObject ("object" in each case substituted by "model").***

    Parameters
    ----------
    city_object_member : CityObjectMember
        ***Description missing***
    gmlid : string
        Unique identifier of CityGML model.
    gmlid_codespace : string
        As it cannot be guarenteed that the gmlid is unique over different
        projects you can specify the codespace.
    name : string
        Each model has a unique name, which is a human readable identifier.
    name_codespace : string
        As it cannot be guarenteed that the name is unique over different
        projects you can specify the codespace.
    description : string
        A string that gives additional information about the model.
    envelope : Polygon
        The Envelope is realized as rectangular geometry using five points,
        that join the minimum and maximum x, y and z coordinates of the
        envelope and define it (usage not recommended).
    creation_date : datetime
        Date of entry into the database (do not mix with e.g.
        year_of_construction of building).
    termination_date : datetime
        Date of termination of the city model.
    last_modification_date : datetime
        Date of modification.
    updating_person : string
        Name of last updating person.
    reason_for_update : string
        Give a reason for updates.
    lineage : string
        Source of data that has been inserted/updated.

    """

    city_object_member = models.ManyToManyField(
        CityObject, blank=True, through="CityObjectMember", related_name="city_model"
    )
    gmlid = models.CharField(max_length=256, blank=True, null=True)
    gmlid_codespace = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    name_codespace = models.CharField(max_length=4000, blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    envelope = models.PolygonField(srid=31468, dim=3, blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)
    termination_date = models.DateTimeField(blank=True, null=True)
    last_modification_date = models.DateTimeField(blank=True, null=True)
    updating_person = models.CharField(max_length=256, blank=True, null=True)
    reason_for_update = models.CharField(max_length=4000, blank=True, null=True)
    lineage = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        """Metaclass of CityModel."""

        managed = False
        db_table = "citymodel"


class CityObjectMember(models.Model):
    """ORM class for city_object_member table from 3DCityDB.

    ***Description missing***

    Parameters
    ----------
    citymodel : CityModel
        Foreign key to the corresponding CityModel instance.
    cityobject : CityObject
        Foreign key to the corresponding CityObject instance.

    """

    citymodel = models.ForeignKey(CityModel, models.DO_NOTHING, primary_key=True)
    cityobject = models.ForeignKey(CityObject, models.DO_NOTHING)

    class Meta:
        """Metaclass of CityObjectMember."""

        managed = False
        auto_created = True
        db_table = "cityobject_member"
        unique_together = (("citymodel", "cityobject"),)


@receiver(pre_delete, sender=CityModel, dispatch_uid="delete_city_model")
def delete_city_model(sender, instance, **kwargs):
    """Django singal to interact with Influx database.

    Deletes the dataframe given as values from InfluxDB.
    """
    instance.city_object_member.clear()
