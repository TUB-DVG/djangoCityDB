"""This module contains the class WeatherData from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from citydb.modules.energy.timeseries.timeseries import TimeSeries
from citydb.modules.energy.core.weatherstation import WeatherStation
from django.contrib.gis.db import models


class WeatherData(CityObject):
    """ORM class for weather_data table from EnergyADE.

    Data structure to model weather or climate data at the location of a building.

    Parameters
    ----------
    position : Point
        Measurement position.
    values : ForeignKey
        Time series of data.
    weather_data_type_choices : tuple
        Type choices for weather_data_type.
    weather_data_type : String
        Type of the meteorological or physical parameter.
    weatherstation_parameter : ForeignKey
        Foreign key to the the corresponding WeatherStation instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="weather_data_obj",
    )

    position = models.PointField(
        db_column="position", srid=25832, dim=3, blank=True, null=True
    )
    values = models.ForeignKey(
        TimeSeries,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="values_id",
        related_name="weather_values",
    )
    weather_data_type_choices = (
        ("precipitationIntensity", "precipitationIntensity"),
        ("precipitationQuantity", "precipitationQuantity"),
        ("dewPointTemperature", "dewPointTemperature"),
        ("airTemperature", "airTemperature"),
        ("windSpeed", "windSpeed"),
        ("windDirection", "windDirection"),
        ("airPressure", "airPressure"),
        ("humidity", "humidity"),
        ("windSpeed", "windSpeed"),
        ("cloudiness", "cloudiness"),
        ("globalSolarIrradiance", "globalSolarIrradiance"),
        ("directSolarIrradiance", "directSolarIrradiance"),
        ("diffuseSolarIrradiance", "diffuseSolarIrradiance"),
        ("terrestrialEmission", "terrestrialEmission"),
        ("downwardTerrestrialRadiation", "downwardTerrestrialRadiation"),
        ("daylightIlluminance", "daylightIlluminance"),
    )

    weather_data_type = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        db_column="weatherdatatype",
        choices=weather_data_type_choices,
    )
    weatherstation_parameter = models.ForeignKey(
        WeatherStation, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        """Metaclass of WeatherData."""

        managed = False
        db_table = "ng_weatherdata"
