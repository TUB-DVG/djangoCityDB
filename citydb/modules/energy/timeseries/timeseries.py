"""This module contains the class TimeSeries and the derived class IrregularTimeSeriesFile from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.core.objectclass import ObjectClass
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from datetime import datetime as dt
from django.conf import settings
import warnings
import numpy as np
import influxdb
import time
import os
import pandas as pd
# import calibration.utils.owncloud as owncloud


class TimeSeries(CityObject):
    """ORM class for time_series table from EnergyADE.

    Consistent series of time-depending values.

    Parameters:
    -----------
    objectclass_series : ObjectClass
        Foreign key to the corresponding ObjectClass instance.
    am_choices : tuple
        Type choices for acquisition_method.
    acquisition_method : string
        The method for variable acquisition (e.g. simulation, measured).
    interpolation_type : string
        Mathematical rule required for the variable interpolation.
    quality_description : string
        Description of the data quality (e.g. bad, average, good, excellent).
    td_choices : tuple
        Type choices for thematic_description.
    thematic_description : string
        Thematic description of the considered variable (e.g. Power, VolumeFlow).
    source : string
        Designation of the data source.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="timeseries_obj",
    )
    # here we should add Heating, Cooling, Electricity as objectclass

    objectclass_series = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )
    am_choices = (
        ("measurement", "measurement"),
        ("simulation", "simulation"),
        ("calibratedSimulation", "calibratedSimulation"),
        ("estimation", "estimation"),
        ("unknown", "unknown"),
    )
    acquisition_method = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        db_column="timevaluesprop_acquisitionme",
        choices=am_choices,
    )
    interpolation_type = models.CharField(
        max_length=1000, blank=True, null=True, db_column="timevaluesprop_interpolation"
    )
    quality_description = models.CharField(
        max_length=1000, blank=True, null=True, db_column="timevaluesprop_qualitydescri"
    )
    td_choices = (
        ("Power", "Power"),
        ("Energy", "Energy"),
        ("TemperatureDifference", "TemperatureDifference"),
        ("VolumeFlow", "VolumeFlow"),
        ("TotalVolume", "TotalVolume"),
        ("FlowTemperature", "FlowTemperature"),
        ("ReturnTemperature", "ReturnTemperature"),
        ("Schedule", "Schedule"),
        ("AreaSpecificEnergy", "AreaSpecificEnergy"),
    )
    thematic_description = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        db_column="timevaluesprop_thematicdescr",
        choices=td_choices,
    )
    source = models.CharField(
        max_length=1000, blank=True, null=True, db_column="timevaluespropertiest_source"
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for TimeSeries.

        Since 3D CityDB 4.0.0 every TimeSeries has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        
        super(TimeSeries, self).__init__(*args, **kwargs)
        # breakpoint()
        try:
            self.objectclass_series = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate TimeSeries without passing "
                "an ObjectClass"
            )
        

    class Meta:
        """Metaclass of TimeSeries."""

        managed = False
        db_table = "ng_timeseries"


class RegularTimeSeries(TimeSeries):
    """ORM class for regular_time_series table from EnergyADE.

    Time series with constant time increments.

    Parameters:
    -----------
    series_related_to : ObjectClass
        Foreign key to the corresponding ObjectClass instance.
    time_interval : integer
        Time interval between two consecutive time values in seconds.
    uom : string
        Unit of measure of the time series values.
    values : list
        List of time series values.

    """

    _abst_time_series = models.OneToOneField(
        TimeSeries,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="regular_time_series",
    )

    # series_related_to = models.ManyToManyField(
    #     CityObject,
    #     related_name="regular_series",
    #     related_query_name="regular_series",
    # )
    timeinterval = models.IntegerField(
        blank=True, null=True, db_column="timeinterval"
    )
    timeinterval_unit = models.CharField(max_length=1000, blank=True, null=True, db_column="timeinterval_unit")
    timeinterval_factor = models.IntegerField(blank=True, null=True, db_column="timeinterval_factor")
    timeinterval_radix = models.IntegerField(blank=True, null=True, db_column="timeinterval_radix")
    timeperiodprop_beginposition = models.DateTimeField(db_column="timeperiodprop_beginposition")
    timeperiodproper_endposition = models.DateTimeField(db_column="timeperiodproper_endposition")

    values_uom = models.CharField(max_length=1000, blank=True, null=True, db_column="values_uom")
    values = models.TextField(blank=True, null=True, db_column="values_")

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for TimeSeries.

        Since 3D CityDB 4.0.0 every TimeSeries has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        
        super(RegularTimeSeries, self).__init__(*args, **kwargs)
        # breakpoint()
        try:
            self.objectclass_series = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate TimeSeries without passing "
                "an ObjectClass"
            )
        

    class Meta:
        """Metaclass of TimeSeries."""

        managed = False
        db_table = "ng_regulartimeseries"

# class IrregularTimeSeriesFile(TimeSeries):
#     """ORM class for irregular_time_series file table from EnergyADE.

#     Time series with differing time increments, stored in textual format (e.g. CSV)
#     on an external device.

#     Parameters:
#     -----------
#     series_related_to : ObjectClass
#         Foreign key to the corresponding ObjectClass instance.
#     decimal_symbol : string
#         Character used to represent the decimal symbol in floating point numbers.
#     field_separator : string
#         String (e.g. ';') delimiting different fields (e.g. columns in a CSV file) in
#         the same record (e.g. lines in a CSV file).
#     file_id : string
#         URI of the external device containing the time series.
#     number_of_header_lines : insteger
#         Number of header lines in the time series file which must not be interpreted.
#     record_separator : string
#         String (e.g. '\n') separating different records (e.g. lines in a CSV file).
#     time_column_number : integer
#         For CSV files the column number containing the actually used date/time values
#         of the time series.
#     uom : string
#         Unit of measure of the time series values.
#     value_column_number : integer
#         For CSV files the column number containing the actually used time series values.

#     """

#     _abst_time_series = models.OneToOneField(
#         TimeSeries,
#         on_delete=models.CASCADE,
#         db_column="id",
#         primary_key=True,
#         parent_link=True,
#         default=None,
#         related_name="time_series_file",
#     )

#     series_related_to = models.ManyToManyField(
#         CityObject,
#         related_name="irregular_series",
#         related_query_name="irregular_series",
#     )

#     decimal_symbol = models.CharField(
#         max_length=1000, blank=True, null=True, db_column="decimalsymbol"
#     )
#     field_separator = models.CharField(
#         max_length=1000, blank=True, null=True, db_column="fieldseparator"
#     )
#     # Field renamed because it ended with '_'.
#     file_id = models.CharField(
#         db_column="file_", max_length=1000, blank=True, null=True
#     )
#     number_of_header_lines = models.IntegerField(
#         blank=True, null=True, db_column="numberofheaderlines"
#     )
#     record_separator = models.CharField(
#         max_length=1000, blank=True, null=True, db_column="recordseparator"
#     )
#     time_column_number = models.IntegerField(
#         blank=True, null=True, db_column="timecolumnnumber"
#     )
#     uom = models.CharField(max_length=1000, blank=True, null=True, db_column="uom")
#     value_column_number = models.IntegerField(
#         blank=True, null=True, db_column="valuecolumnnumber"
#     )

#     def __init__(self, *args, **kwargs):
#         super(IrregularTimeSeriesFile, self).__init__(*args, **kwargs)
#         self.values = None

#     def get_values(
#         self,
#         start=dt(2014, 1, 1, 0, 0, 0),
#         end=dt.now(),
#         mean="1h",
#         query=None,
#         csv=False,
#         workspace=None,
#         remote_path=None,
#     ):
#         """Perform query to get time series and calculate mean.

#         To get measurement from InfluxDB this function can be called. You can
#         define a time period(given by start and end) and a mean(e.g. 1h).
#         Note, re - calling this function will overwrite old data.

#         Parameters
#         ----------
#         start: datetime.datetime
#             Start time for the time period that is requested. Use python
#             datetime module to generate your start time. Default is
#             01.01.2014 00: 00: 00.
#         time_stamp: datetime.datetime
#             End time for the time period that is requested. Use python
#             datetime module to generate your end time. Default is
#             datetime.now().
#         mean: str or None
#             If you want to specify a mean over a certain time(e.g. 1h) pass
#             the corresponding string. Sensefull means are for example:
#                 '15m': 15 minutes
#                 '1h': 1 hour
#                 '1d': 1 day
#                 ...
#             Default value is '1h'. If you want raw data, pass None.
#         query: str
#             Custom Influx query, if this parameter is set all other parameters
#             will be ignored!

#         """
#         if csv is False:
#             if query is None:
#                 if mean is None:
#                     query_text = """
#                                   SELECT
#                                       *
#                                   FROM
#                                       "{}"
#                                   WHERE
#                                     time >= '{}' AND time <= '{}';""".format(
#                         self.file_id, str(start), str(end)
#                     )

#                 else:
#                     query_text = """
#                                 SELECT
#                                     MEAN(*)
#                                 FROM
#                                     "{}"
#                                 WHERE
#                                     time >= '{}' AND time <= '{}'
#                                 GROUP BY
#                                     time({});""".format(
#                         self.file_id, str(start), str(end), str(mean)
#                     )

#             else:
#                 query_text = query
#             if self.acquisition_method in [
#                 "simulation",
#                 "calibratedSimulation",
#                 "estimation",
#                 "unkown",
#             ]:
#                 self.values = settings.INFLUX_DF_CLIENT_SIM.query(query_text)[
#                     str(self.file_id)
#                 ]
#                 self.values[self.values.columns.values[0]] = self.values[
#                     self.values.columns.values[0]
#                 ].astype(np.float64)
#             else:
#                 self.values = settings.INFLUX_DF_CLIENT.query(query_text)[
#                     str(self.file_id)
#                 ]
#                 self.values[self.values.columns.values[0]] = self.values[
#                     self.values.columns.values[0]
#                 ].astype(np.float64)

#         if csv is True:
#             try:

#                 local_file = os.path.join(workspace, self.file_id + ".csv")

#                 self.values = pd.read_csv(
#                     local_file,
#                     index_col=0,
#                     parse_dates=True,
#                     dtype={self.file_id: np.float64},
#                 ).loc[start:end]

#             except FileNotFoundError:
#                 local_file = os.path.join(workspace, self.file_id + ".csv")

#                 # owncloud.download_from_owncloud(
#                 #     remote_path=remote_path, local_file=local_file
#                 # )

#                 self.values = pd.read_csv(
#                     local_file,
#                     index_col=0,
#                     parse_dates=True,
#                     dtype={self.file_id: np.float64},
#                 ).loc[start:end]
#         return self.values

#     class Meta:
#         """Metaclass of IrregularTimeSeriesFile."""

#         managed = False
#         db_table = "ng_irregulartimeseriesf"


# @receiver(post_save, sender=IrregularTimeSeriesFile, dispatch_uid="save_influx")
# def save_influx(sender, instance, **kwargs):
#     """Django signal to interact with Influx database.

#     Saves the dataframe given as values into InfluxDB.
#     """
#     if instance.values is not None:
#         if isinstance(instance.values, pd.DataFrame):
#             pass
#         elif isinstance(instance.values, pd.Series):
#             instance.values = instance.values.to_frame(instance.file_id)
#         else:
#             warnings.warn(
#                 "Not possible to save/update: {}, because of TypeError".format(
#                     str(instance.file_id)
#                 )
#             )
#         try:
#             if instance.acquisition_method in [
#                 "simulation",
#                 "calibratedSimulation",
#                 "estimation",
#                 "unknown",
#             ]:
#                 try:
#                     settings.INFLUX_DF_CLIENT_SIM.write_points(
#                         instance.values, str(instance.file_id), protocol="json"
#                     )
#                 except influxdb.exceptions.InfluxDBServerError:
#                     time.sleep(120)
#                     try:
#                         settings.INFLUX_DF_CLIENT_SIM.write_points(
#                             instance.values, str(instance.file_id), protocol="json"
#                         )
#                     except influxdb.exceptions.InfluxDBServerError:
#                         warnings.warn(
#                             "Not possible to save/update: {}, because of InfluxDBServerError, which probably means influxdb docker is broke".format(
#                                 str(instance.file_id)
#                             )
#                         )
#             else:
#                 settings.INFLUX_DF_CLIENT.write_points(
#                     instance.values, str(instance.file_id), protocol="json"
#                 )
#             print("{} saved".format(instance.file_id))
#         except (KeyError, AttributeError, TypeError):
#             warnings.warn(
#                 "Not possible to save/update: {}, because of KeyError, AttributeError or TypeError, which probably means that there is something wrong with measurement in influxdb".format(
#                     str(instance.file_id)
#                 )
#             )


# @receiver(pre_delete, sender=IrregularTimeSeriesFile, dispatch_uid="delete_influx")
# def delete_influx(sender, instance, **kwargs):
#     """Django signal to interact with Influx database.

#     Deletes the dataframe given as values from InfluxDB.
#     """
#     try:
#         if instance.acquisition_method in [
#             "simulation",
#             "calibratedSimulation",
#             "estimation",
#             "unknown",
#         ]:
#             settings.INFLUX_DF_CLIENT_SIM.delete_series(measurement=instance.file_id)
#         else:
#             settings.INFLUX_DF_CLIENT.delete_series(measurement=instance.file_id)
#         print("{} deleted".format(instance.file_id))
#     except (KeyError, AttributeError):
#         pass
