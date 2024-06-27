"""This module contains the class LayerComponent from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.core.cityobject import CityObject
from citydb.modules.energy.materials.layer import Layer
from citydb.modules.energy.materials.material import AbstractMaterial
from citydb.modules.energy.core.servicelife import ServiceLife


class LayerComponent(CityObject):
    """ORM class for layer_component table from EnergyADE.

    One Layer can consist of several layer components.

    Parameters:
    -----------
    area_fraction : float
        Portion of the layer area that is made from the referenced
        Material, must be between 0 and 1.
    area_fraction_uom : string
        Defines the unit of measurement of area_fraction.
    layer : Layer
        Foreign key to the corresponding Layer instance.
    material : AbstractMaterial
        Foreign key to the corresponding AbstractMaterial instance.
    service_life : ServiceLife
        Foreign key to the corresponding ServiceLife instance.
    thickness : float [***]
        Thickness of the layer component.
    thickness_uom : string
        Defines the unit of measurement of thickness, should always be [***].

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="layer_component_obj",
    )
    area_fraction = models.FloatField(db_column="areafraction", blank=True, null=True)
    area_fraction_uom = models.CharField(
        db_column="areafraction_uom", max_length=1000, blank=True, null=True
    )
    layer = models.ForeignKey(
        Layer,
        models.CASCADE,
        db_column="layer_layercomponent_id",
        blank=True,
        null=True,
        related_name="layer_component",
    )
    material = models.ForeignKey(
        AbstractMaterial,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="layer_component_material",
    )
    service_life = models.ForeignKey(
        ServiceLife,
        models.CASCADE,
        db_column="servicelife_id",
        blank=True,
        null=True,
        related_name="layer_component_service_life",
    )
    thickness = models.FloatField(blank=True, null=True)
    thickness_uom = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        """Metaclass of LayerComponent."""

        managed = False

        db_table = "ng_layercomponent"
