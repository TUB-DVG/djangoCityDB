"""This module contains the class Layer from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.core.cityobject import CityObject
from citydb.modules.energy.materials.construction import Construction


class Layer(CityObject):
    """ORM class for layer table from EnergyADE.

    A Layer is a combination of one or more materials, references via a LayerComponent.

    Parameters:
    -----------
    construction : Construction
        Foreign key to the corresponding Construction instance.
    ordered_position : integer
        Ordered position of the layer in the construction, starting from 1 on
        the inside surface.


    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="layer_obj",
    )
    construction = models.ForeignKey(
        Construction,
        models.CASCADE,
        blank=True,
        null=True,
        db_column="construction_layer_id",
        related_name="layer",
    )
    ordered_position = models.IntegerField(blank=True, null=True)

    class Meta:
        """Metaclass of Layer."""

        managed = False
        db_table = "ng_layer"
