"""This module contains the class ThermalZone from EnergyADE."""
from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.energy.core.energybuilding import EnergyBuilding
from citydb.modules.geometry.surface_geometry import SurfaceGeometry


class ThermalZone(CityObject):
    """ORM class for thermal_zone table from EnergyADE.

    The ThermalZone inherits from CityObject, thus all attributes of CityObject
    are directly accessible through ThermalZone.

    A thermal zone is the smallest spatial zone in a building.

    Parameters
    ----------
    building : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.
    additional_thermal_bridge_u_value : Decimal [W/m²K]
        Surplus to the overall U-Value of the thermal zone because of thermal
        bridges.
    additional_thermal_bridge_u_value_uom : string
        Defines the unit of measurement of additional_thermal_bridge_u_value,
        should always be [W/m²K].
    effective_thermal_capacity : Decimal [J/kgK]
        Thermal active thermal capacity of thermal zone.
    effective_thermal_capacity_uom : string
        Defines the unit of measurement of effective_thermal_capacity, should always be
        [J/kgK].
    indirectly_heated_area_ratio : Decimal
        ***Description missing***, must be between 0 and 1.
    indirectly_heated_area_ratio_uom : string
        Defines the unit of measurement of indirectly_heated_area_ratio.
    infiltration_rate : float [1/h]
        Natural infiltration rate of the thermal zone.
    infiltration_rate_uom : string
        Defines the unit of measurement of infiltration_rate, should always be
        [1/h].
    volume_geometry : SurfaceGeometry
        Geometrical representation of the ThermalZone volume.
    is_cooled : Boolean
        Decision if the thermal zone is actively cooled.
    is_heated : Boolean
        Decision if the thermal zone is actively heated.
    is_ventilated : Boolean
        Decision if the thermal zone is actively ventilated.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="thermal_zone_obj",
    )
    _is_cooled = models.IntegerField(db_column="iscooled", blank=True, null=True)
    _is_heated = models.IntegerField(db_column="isheated", blank=True, null=True)
    _is_ventilated = models.IntegerField(
        db_column="isventilated", blank=True, null=True
    )
    building = models.ForeignKey(
        EnergyBuilding,
        models.CASCADE,
        db_column="building_thermalzone_id",
        blank=True,
        null=True,
        related_name="thermal_zones",
    )
    additional_thermal_bridge_uvalue = models.DecimalField(
        db_column="additionalthermalbridgeuvalu",
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    additional_thermal_bridge_u_value_uom = models.CharField(
        db_column="additionalthermalbridgeu_uom", max_length=1000, blank=True, null=True
    )
    effective_thermal_capacity = models.DecimalField(
        db_column="effectivethermalcapacity",
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    effective_thermal_capacity_uom = models.CharField(
        db_column="effectivethermalcapacity_uom", max_length=1000, blank=True, null=True
    )
    indirectly_heated_area_ratio = models.DecimalField(
        db_column="indirectlyheatedarearatio",
        max_digits=65535,
        decimal_places=65535,
        blank=True,
        null=True,
    )
    indirectly_heated_area_ratio_uom = models.CharField(
        db_column="indirectlyheatedarearati_uom", max_length=1000, blank=True, null=True
    )
    infiltration_rate = models.FloatField(
        db_column="infiltrationrate", blank=True, null=True
    )
    infiltration_rate_uom = models.CharField(
        db_column="infiltrationrate_uom", max_length=1000, blank=True, null=True
    )
    volume_geometry = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        db_column="volumegeometry_id",
        blank=True,
        null=True,
        related_name="volume_geometry_tz",
    )

    class Meta:
        """Metaclass of ThermalZone."""

        managed = False

        db_table = "ng_thermalzone"

    @property
    def floor_area(self):
        """Return floor_area."""
        value = self.floor_area_tz.get(type="netFloorArea").value
        return float(value)

    @floor_area.setter
    def floor_area(self, value):
        """Set floor_area."""
        from citydb.models import FloorArea

        FloorArea(
            thermal_zone=self, type="netFloorArea", value=value, value_uom="sqm"
        ).save()

    @property
    def volume(self):
        """Return volume."""
        value = self.volume_tz.get(type="netVolume").value
        return float(value)

    @volume.setter
    def volume(self, value):
        """Set volume."""
        from citydb.models import VolumeType

        VolumeType(
            thermal_zone=self, type="netVolume", value=value, value_uom="m3"
        ).save()

    @property
    def is_heated(self):
        """Return _is_heated.

        Value is 1 if thermal zone has energy system for space
        heating, else 0.
        """
        translate = {0: False, 1: True}
        value = translate[self._is_heated]
        return value

    @is_heated.setter
    def is_heated(self, value):
        """Set _is_heated.

        Value is 1 if thermal zone has energy system for space
        heating, else 0.
        """
        translate = {False: 0, True: 1}
        self._is_heated = translate[value]

    @property
    def is_cooled(self):
        """Return _is_cooled.

        Value is 1 if thermal zone has energy system for space
        cooling, else 0.
        """
        translate = {0: False, 1: True}
        value = translate[self._is_cooled]
        return value

    @is_cooled.setter
    def is_cooled(self, value):
        """Set _is_cooled.

        Value is 1 if thermal zone has energy system for space
        cooling, else 0.
        """
        translate = {False: 0, True: 1}
        self._is_cooled = translate[value]

    @property
    def is_ventilated(self):
        """Return _is_ventilated.

        Value is 1 if thermal zone has energy system for space
        cooling, else 0.
        """
        translate = {0: False, 1: True}
        value = translate[self._is_ventilated]
        return value

    @is_ventilated.setter
    def is_ventilated(self, value):
        """Set _is_ventilated.

        Value is 1 if thermal zone has energy system for space
        cooling, else 0.
        """
        translate = {False: 0, True: 1}
        self._is_ventilated = translate[value]
