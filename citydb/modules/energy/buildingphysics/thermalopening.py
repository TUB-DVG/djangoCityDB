"""This module contains the class ThermalOpening from EnergyADE."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from citydb.modules.bldg.opening import Opening
from citydb.modules.energy.buildingphysics.thermalboundary import ThermalBoundary
from citydb.modules.energy.buildingphysics.shadingtype import ShadingType
from citydb.modules.energy.materials.construction import Construction


class ThermalOpening(CityObject):
    """ORM class for thermal_opening table from EnergyADE.

    A thermal opening is the transparent counter part to a thermal boundary.

    The ThermalOpening inherits from CityObject, thus all attributes of CityObject are
    directly accessible through ThermalOpening.

    Parameters
    ----------
    area : float [m²]
        Area of the surface, portion of the related thermal boundary surface.
    area_uom : string
        Defines the unit of measurement of area, should always be [m²].
    construction : Construction
        Foreign key to the corresponding Construction instance.
    indoor_shading : ShadingType
        Shading system installed on the interior surface of the opening.
    openable_ratio : float
        The openable ratio characterizes the proportion of the opening area
        which may be opened, must be between 0 and 1.
    openable_ratio_uom : string
        Defines the unit of measurement of openable_ratio.
    outdoor_shading : ShadingType
        Shading system installed on the outside opening surface.
    surface_geometry : SurfaceGeometry
        Foreign key to the corresponding SurfaceGeometry instance.
    thermal_boundary : ThermalBoundary
        Every ThermalOpening is connected to a thermal_boundary.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="thermal_opening_obj",
    )
    area = models.FloatField(blank=True, null=True)
    area_uom = models.CharField(max_length=1000, blank=True, null=True)
    construction = models.ForeignKey(
        Construction,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="construction_to",
    )
    indoor_shading = models.ForeignKey(
        ShadingType,
        models.CASCADE,
        db_column="indoorshading_id",
        blank=True,
        null=True,
        related_name="indoor_shading_to",
    )
    openable_ratio = models.FloatField(db_column="openableratio", blank=True, null=True)
    openable_ratio_uom = models.CharField(
        db_column="openableratio_uom", max_length=1000, blank=True, null=True
    )
    outdoor_shading = models.ForeignKey(
        ShadingType,
        models.CASCADE,
        db_column="outdoorshading_id",
        blank=True,
        null=True,
        related_name="outdoor_shading_to",
    )
    surface_geometry = models.ForeignKey(
        SurfaceGeometry,
        db_column="surfacegeometry_id",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="surface_geometry_to",
    )
    thermal_boundary = models.ForeignKey(
        ThermalBoundary,
        on_delete=models.CASCADE,
        db_column="thermalboundary_contains_id",
        blank=True,
        null=True,
        related_name="contains",
    )

    class Meta:
        """Meta Class of ThermalOpening."""

        managed = False
        db_table = "ng_thermalopening"


class ThermalOpeningToOpening(models.Model):
    """A mapping table to manage the relations of thermal openings and openings.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    opening = models.ForeignKey(
        Opening, models.DO_NOTHING, primary_key=True, related_name="opening"
    )
    thermal_opening = models.ForeignKey(
        ThermalOpening,
        models.DO_NOTHING,
        db_column="thermalopening",
        related_name="relates_to_opening",
    )

    class Meta:
        """Meta Class of ThermalOpeningToOpening."""

        managed = False
        auto_created = True
        db_table = "ng_thermalop_to_opening"
        unique_together = (("opening", "thermal_opening"),)
