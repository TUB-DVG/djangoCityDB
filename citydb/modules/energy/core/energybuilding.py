"""This module contains the class EnergyBuilding from EnergyADE."""

import citydb.modules.bldg.building as bldg
from django.contrib.gis.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class EnergyBuilding(models.Model):
    """ORM class for energy_building table from EnergyADE.

    The EnergyBuilding extends the CityGML Building and adds energy related
    attributes.

    Please use this class for all buildings.

    Parameters
    ----------
    bt_type_choices : tuple
        Type choices for building_type.
    building_type : string
        Building type can follow several typologies, e.g. TABULA or BMVBS.
    building_type_codespace : string
        Describes the used methodology for building_type.
    ct_type_choices : tuple
        Type choices for construction_weight.
    construction_weight : string
        Qualitative classifier of the thermal capacity of the building.
    reference_point : Geometry
        Reference point (most likely the middle) of the building.

    """

    _parent_link_eb = models.OneToOneField(
        bldg.Building,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="building_energy_obj",
    )
    # _is_landmarked = models.DecimalField(
    #     db_column="islandmarked",
    #     max_digits=65535,
    #     decimal_places=65535,
    #     blank=True,
    #     null=True,
    # )
    bt_type_choices = (
        ("Office", "Office"),
        ("Institute", "Institute"),
        ("Institute4", "Institute4"),
        ("Institute8", "Institute8"),
        ("SingleFamilyDwelling", "SingleFamilyDwelling"),
        ("SingleFamilyHouse", "SingleFamilyHouse"),
        ("MultiFamilyHouse", "MultiFamilyHouse"),
        ("Apartmentblock", "Apartmentblock"),
    )
    building_type = models.CharField(
        db_column="buildingtype",
        max_length=1000,
        blank=True,
        null=True,
        choices=bt_type_choices,
    )
    building_type_codespace = models.CharField(
        db_column="buildingtype_codespace", max_length=1000, blank=True, null=True
    )
    ct_type_choices = (
        ("veryLight", "veryLight"),
        ("light", "light"),
        ("medium", "medium"),
        ("heavy", "heavy"),
    )
    construction_weight = models.CharField(
        db_column="constructionweight",
        max_length=1000,
        blank=True,
        null=True,
        choices=ct_type_choices,
    )
    # is_landmarked = models.DecimalField(
    #     db_column="islandmarked",
    #     max_digits=65535,
    #     decimal_places=65535,
    #     blank=True,
    #     null=True,
    # )
    reference_point = models.PointField(
        db_column="referencepoint", srid=25832, dim=3, blank=True, null=True
    )

    class Meta:
        """Metaclass of EnergyBuilding."""

        managed = False
        db_table = "ng_building"

    @property
    def floor_area(self):
        """Return floor_area."""
        value = self.floor_area_bldg.get(type="netFloorArea").value
        return float(value)

    @floor_area.setter
    def floor_area(self, value):
        """Set floor_area."""
        from citydb.models import FloorArea

        FloorArea(
            building=self, type="netFloorArea", value=value, value_uom="sqm"
        ).save()

    @property
    def volume(self):
        """Return volume."""
        value = self.volume_bldg.get(type="netVolume").value
        return float(value)

    @volume.setter
    def volume(self, value):
        """Set volume."""
        from citydb.models import VolumeType

        VolumeType(building=self, type="netVolume", value=value, value_uom="m3").save()

    @property
    def height_above_ground(self):
        """Return height_above_ground."""
        value = self.height_above_ground_bldg.get(height_reference="highestPoint").value
        return value

    @height_above_ground.setter
    def height_above_ground(self, value):
        """Set height_above_ground."""
        from citydb.models import HeightAboveGround

        HeightAboveGround(
            building=self, height_reference="highestPoint", value=value, value_uom="m"
        ).save()

    @property
    def is_landmarked(self):
        """Return _is_landmarked.

        Value is 1 if the building is under landmark protection, else 0.
        """
        translate = {0: False, 1: True}
        value = translate[self._is_landmarked]
        return value

    @is_landmarked.setter
    def is_landmarked(self, value):
        """Set _is_landmarked.

        Value is 1 if the building is under landmark protection, else 0.
        """
        translate = {False: 0, True: 1}
        self._is_landmarked = translate[value]


@receiver(pre_delete, sender=EnergyBuilding, dispatch_uid="delete_building")
def delete_building(sender, instance, **kwargs):
    """Django singal to interact with Influx database.

    Deletes the dataframe given as values from InfluxDB
    """
    from citydb.models import HeightAboveGround
    from citydb.models import VolumeType
    from citydb.models import FloorArea

    try:
        hag = instance.height_above_ground_bldg.filter(building=instance)
        hag.delete()
    except HeightAboveGround.DoesNotExist:
        pass
    try:
        vol = instance.volume_bldg.filter(building=instance)
        vol.delete()
    except VolumeType.DoesNotExist:
        pass
    try:
        area = instance.floor_area_bldg.filter(building=instance)
        area.delete()
    except FloorArea.DoesNotExist:
        pass
