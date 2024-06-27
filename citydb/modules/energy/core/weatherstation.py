"""This module contains the class WeatherStation from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models


class WeatherStation(models.Model):
    """ORM class for weather_station table from EnergyADE.

    Information on a weather station providing weather data.

    Parameters
    ----------
    position : Point
        Position of the weather station.
    station_name . string
        Name of the weather station.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="weather_station_obj",
    )
    position = models.PointField(
        db_column="position", srid=25832, dim=3, blank=True, null=True
    )
    station_name = models.CharField(
        max_length=1000, blank=True, null=True, db_column="stationname"
    )

    class Meta:
        """Metaclass of WeatherStation."""

        managed = False
        db_table = "ng_weatherstation"
