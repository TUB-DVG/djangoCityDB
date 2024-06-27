"""This module contains the class ObjectClass from 3DCityDB."""

from django.contrib.gis.db import models


class ObjectClass(models.Model):
    """ORM class for object_class table from 3DCityDB.

    ObjectClass is used to efficiently determine the affiliation to a class in
    the superclass tables.

    Parameters
    ----------
    classname : string
        Name of the CityGML table.
    superclass : ObjectClass
        Foreign key to the parent Objectclass this class inherits from.

    """

    classname = models.CharField(max_length=256, blank=True, null=True)
    superclass = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        """Return object class."""
        return "{} (ObjectClass)".format(self.classname)

    class Meta:
        """Metaclass of ObjectClass."""

        managed = False
        db_table = "objectclass"
