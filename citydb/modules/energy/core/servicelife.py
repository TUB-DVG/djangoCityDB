"""This module contains the class ServiceLife from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models


class ServiceLife(CityObject):
    """ORM class for service_life table from EnergyADE.

    Information on product life time and maintenance intervals.

    Parameters
    ----------
    lifeexpectancy : Decimal
        Length of the service life of a product which is expected at its installation
        or construction.
    lifeexpectancy_factor : integer
        ***Description missing.***
    lifeexpectancy_radix : integer
        ***Description missing.***
    lifeexpectancy_unit : string
        ***Description missing.***
    mainmaintenanceinterv_factor : integer
        ***Description missing.***
    mainmaintenanceinterva_radix : integer
        ***Description missing.***
    mainmaintenanceinterval : Decimal
        Average period of time between two consecutive main maintenance operations.
    mainmaintenanceinterval_unit : string
        ***Description missing.***
    startoflife : string
        Date where a product has been put into service for the first time (e.g.
        installation, construction).
    startoflife_calendareraname : string
        ***Description missing.***
    startoflife_frame : string
        ***Description missing.***
    startoflife_indeterminatepos : string
        ***Description missing.***

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="service_life_obj",
    )
    lifeexpectancy = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    lifeexpectancy_factor = models.IntegerField(blank=True, null=True)
    lifeexpectancy_radix = models.IntegerField(blank=True, null=True)
    lifeexpectancy_unit = models.CharField(max_length=1000, blank=True, null=True)
    mainmaintenanceinterv_factor = models.IntegerField(blank=True, null=True)
    mainmaintenanceinterva_radix = models.IntegerField(blank=True, null=True)
    mainmaintenanceinterval = models.DecimalField(
        max_digits=65535, decimal_places=65535, blank=True, null=True
    )
    mainmaintenanceinterval_unit = models.CharField(
        max_length=1000, blank=True, null=True
    )
    startoflife = models.CharField(max_length=1000, blank=True, null=True)
    startoflife_calendareraname = models.CharField(
        max_length=1000, blank=True, null=True
    )
    startoflife_frame = models.CharField(max_length=1000, blank=True, null=True)
    startoflife_indeterminatepos = models.CharField(
        max_length=1000, blank=True, null=True
    )

    class Meta:
        """Metaclass of ServiceLife."""

        managed = False
        db_table = "ng_servicelife"
