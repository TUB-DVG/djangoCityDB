"""This module contains the class TimeSeriesSchedule from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.core.objectclass import ObjectClass
from citydb.modules.energy.timeseries.timeseries import TimeSeries


class TimeSeriesSchedule(CityObject):
    """ORM class for time_series_schedule table from EnergyADE.

    Highest Level of Detail of the schedule representation, consisting in a Timeseries.

    Parameters:
    -----------
    average_value : Decimal
        Average value of the considered variable.
    average_value_uom : string
        Defines the unit of measurement of average_value.
    objectclass_schedule : ObjectClass
        Foreign key to the corresponding ObjectClass instance.
    time_depending_values : TimeSeries
        Foreign key to the corresponding TimeSeries instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="schedule_obj",
    )
    # average_value = models.DecimalField(
    #     max_digits=65535,
    #     decimal_places=65535,
    #     blank=True,
    #     null=True,
    #     db_column="averagevalue",
    # )
    # average_value_uom = models.CharField(
    #     max_length=1000, blank=True, null=True, db_column="averagevalue_uom"
    # )
    # objectclass_schedule = models.ForeignKey(
    #     ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    # )
    # time_depending_values = models.ForeignKey(
    #     TimeSeries,
    #     models.CASCADE,
    #     blank=True,
    #     null=True,
    #     db_column="timedependingvalues_id",
    #     related_name="schedule_time_depending_obj",
    # )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for TimeSeriesSchedule.

        Since 3D CityDB 4.0.0 every TimeSeriesSchedule has its own
        objectclass id. Since Django does not allow overwriting inherited
        fields, we must catch this manually.
        """
        super(TimeSeriesSchedule, self).__init__(*args, **kwargs)
        try:
            self.objectclass_schedule = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate TimeSeriesSchedule without "
                + "passing an ObjectClass"
            )

    class Meta:
        """Metaclass for TimeSeriesSchedule."""

        managed = False
        db_table = "ng_schedule"

class NgPeriodOfYear(models.Model):
    id = models.AutoField(primary_key=True, db_column="id")
    objectclass_id = models.ForeignKey(ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE, blank=True, null=True)
    schedule_periodofyear_id = models.ForeignKey(TimeSeriesSchedule, db_column="schedule_periodofyear_id", on_delete=models.CASCADE)
    timeperiodprop_beginposition = models.DateTimeField(db_column="timeperiodprop_beginposition")
    timeperiodproper_endposition = models.DateTimeField(db_column="timeperiodproper_endposition")

    # def __init__(self, *args, **kwargs):
    #     """Catch ObjectClass Forgein key for NgPeriodOfYear.

    #     Since 3D CityDB 4.0.0 every TimeSeriesSchedule has its own
    #     objectclass id. Since Django does not allow overwriting inherited
    #     fields, we must catch this manually.
    #     """
    #     super(NgPeriodOfYear, self).__init__(*args, **kwargs)
    #     try:
    #         self.objectclass_schedule = self.objectclass
    #     except ObjectClass.DoesNotExist:
    #         raise ObjectClass.DoesNotExist(
    #             "You should never instantiate TimeSeriesSchedule without "
    #             + "passing an ObjectClass"
    #         )
    class Meta:
        managed = False
        db_table = "ng_periodofyear"

class DailySchedule(models.Model):
    """ORM class for daily_schedule table from EnergyADE.
    """
    id = models.AutoField(primary_key=True, db_column="id")
    daytype = models.CharField(1000, blank=True, null=True, db_column="daytype")
    periodofyear_dailyschedul_id = models.ForeignKey(NgPeriodOfYear, on_delete=models.CASCADE, blank=True, null=True, db_column="periodofyear_dailyschedul_id")
    schedule_id = models.ForeignKey(TimeSeries, db_column="schedule_id", on_delete=models.CASCADE)

    # def __init__(self, *args, **kwargs):
    #     """Catch ObjectClass Forgein key for TimeSeriesSchedule.

    #     Since 3D CityDB 4.0.0 every TimeSeriesSchedule has its own
    #     objectclass id. Since Django does not allow overwriting inherited
    #     fields, we must catch this manually.
    #     """
    #     super(DailySchedule, self).__init__(*args, **kwargs)
    #     breakpoint()
    #     try:
    #         self.objectclass_schedule = self.objectclass
    #     except ObjectClass.DoesNotExist:
    #         raise ObjectClass.DoesNotExist(
    #             "You should never instantiate TimeSeriesSchedule without "
    #             + "passing an ObjectClass"
    #         )

    class Meta:
        managed = False
        db_table = "ng_dailyschedule"