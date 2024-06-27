"""This module contains the class HeatExchangeType from EnergyADE."""
from django.contrib.gis.db import models
from django.db import connection


def sequence_id():
    """Get next value of floor_area sequence."""

    with connection.cursor() as cursor:

        cursor.execute("""SELECT nextval('ng_heatexchangetype_seq')""")
        return cursor.fetchone()[0]


class HeatExchangeType(models.Model):
    """ORM class for heat_exchange_type table from EnergyADE.

    Contributions of the different types of heat or cool exchange (convective, radiant
    and latent).

    Parameters
    ----------
    convective_fraction : Decimal
        Ratio of convective heat exchange over total heat exchange, must be between 0
        and 1.
    convective_fraction_uom : string
        Defines the unit of measurement of convective_fraction.
    latent_fraction : Decimal
        Ratio of latent heat exchange over total heat exchange, must be between 0 and 1.
    latent_fraction_uom : string
        Defines the unit of measurement of latent_fraction.
    radiant_fraction : Decimal
        Ratio of radiant heat exchange over total heat exchange, must be between 0 and
        1.
    radiant_fraction_uom : string
        Defines the unit of measurement of radiant_fraction.
    total_value : Decimal [***]
        Total heat exchange value (positve for heat source, negative for heat sink/cool
        source).
    total_value_uom : string
        Defines the unit of measurement of total_value, should always be [***].

    """

    id = models.IntegerField(db_column="id", primary_key=True, default=sequence_id)
    convective_fraction = models.FloatField(
        blank=True, null=True, db_column="convectivefraction"
    )
    convective_fraction_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="convectivefraction_uom"
    )
    latent_fraction = models.FloatField(
        blank=True, null=True, db_column="latentfraction"
    )
    latent_fraction_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="latentfraction_uom"
    )
    radiant_fraction = models.FloatField(
        blank=True, null=True, db_column="radiantfraction"
    )
    radiant_fraction_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="radiantfraction_uom"
    )
    total_value = models.FloatField(blank=True, null=True, db_column="totalvalue")
    total_value_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="totalvalue_uom"
    )

    class Meta:
        """Metaclass of HeatExchangeType."""

        managed = False
        db_table = "ng_heatexchangetype"
