"""This module contains the class ThermalBoundary from EnergyADE."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from citydb.modules.geometry.thematic_surface import ThematicSurface
from citydb.modules.energy.buildingphysics.thermalzone import ThermalZone
from citydb.modules.energy.materials.construction import Construction


class ThermalBoundary(CityObject):
    """ORM class for thermal_boundary table from EnergyADE.

    The ThermalBoundary inherits from CityObject, thus all attributes of CityObject are
    directly accessible through ThermalBoundary.

    A Thermal Boundary is a wall, door etc.

    Parameters
    ----------
    area : float [m²]
        Total area of the Thermal Boundary, inclusive the included opening area.
    area_uom : string
        Defines the unit of measurement of area, should always be [m²].
    azimuth : float [degree]
        Azimuth orientation of the boundary, where 0 is north and 180 is south.
    azimuth_uom : string
        Defines the unit of measurement of azimuth, should always be [degree].
    construction : Construction
        Foreign key to the construction details of the thermal boundary.
    inclination : float [degree]
        Tilt of the boundary, where 0 is horizontal an 90 vertical.
    inclination_uom : string
        Defines the unit of measurement of inclination, should always be [degree].
    surface_geometry : SurfaceGeometry
        Foreign key to a geometric representation of the Thermal Boundary.
    tb_type_choices : tuple
        Type choices for thermal_boundary_type.
    thermal_boundary_type : string
        Identifier to distinguish between different Thermal Boundaries.
    delimites : ThermalZone
        In case two ThermalZones are referenced via the relation "delimits", the
        following rule concerning the order of the related objects applys:
            For ThermalBoundary objects of type "intermediateFloor", the first related
            object is the upper ThermalZone, and the seconr related object is the lower
            ThermalZone.
            For all other ThermalBoundary types, the first related ThermalZone is in
            contact with the last Layer of the corresponding AbstractConstruction, and
            the second related ThermalZone is in contact with the first Layer of the
            corresponding AbstractConstruction.
    relates_to : ThematicSurface
        Reference of a Thermal Boundary to the corresponding physical boundary surface
        of the building.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="thermal_boundary_obj",
    )
    area = models.FloatField(blank=True, null=True)
    area_uom = models.CharField(max_length=1000, blank=True, null=True)
    azimuth = models.FloatField(blank=True, null=True)
    azimuth_uom = models.CharField(max_length=1000, blank=True, null=True)
    construction = models.ForeignKey(
        Construction,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="construction_tb",
    )
    inclination = models.FloatField(blank=True, null=True)
    inclination_uom = models.CharField(max_length=1000, blank=True, null=True)
    surface_geometry = models.ForeignKey(
        SurfaceGeometry,
        db_column="surfacegeometry_id",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="surface_geometry_tb",
    )
    tb_type_choices = (
        ("interiorWall", "interiorWall"),
        ("intermediateFloor", "intermediateFloor"),
        ("intermediateCeiling", "intermediateCeiling"),
        ("sharedWall", "sharedWall"),
        ("outerWall", "outerWall"),
        ("door", "door"),
        ("groundSlab", "groundSlab"),
        ("basementCeiling", "basementCeiling"),
        ("atticFloor", "atticFloor"),
        ("roof", "roof"),
    )
    thermal_boundary_type = models.CharField(
        db_column="thermalboundarytype",
        max_length=1000,
        blank=True,
        null=True,
        choices=tb_type_choices,
    )
    delimites = models.ManyToManyField(
        ThermalZone,
        blank=True,
        through="ThermalZoneToThermalBoundary",
        related_name="thermal_boundary_obj",
    )
    relates_to = models.ManyToManyField(
        ThematicSurface, through="ThermalBoundaryToThematicSurface"
    )

    class Meta:
        """Metaclass of ThermalBoundary."""

        managed = False
        db_table = "ng_thermalboundary"


class ThermalZoneToThermalBoundary(models.Model):
    """A mapping table to manage the relations of thermal zones and thermal boundaries.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    thermal_boundary = models.ForeignKey(
        ThermalBoundary,
        models.CASCADE,
        db_column="thermalboundary_delimits_id",
        primary_key=True,
    )
    thermal_zone = models.ForeignKey(
        ThermalZone,
        models.CASCADE,
        db_column="thermalzone_boundedby_id",
        related_name="bounded_by",
    )

    class Meta:
        """Metaclass of ThermalZoneToThermalBoundary."""

        managed = False
        auto_created = True
        db_table = "ng_ther_deli_to_the_bou"
        unique_together = (("thermal_boundary", "thermal_zone"),)


class ThermalBoundaryToThematicSurface(models.Model):
    """A mapping table to manage the relations of thermal boundaries and thematic surfaces.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    thematic_surface = models.ForeignKey(
        ThematicSurface,
        models.CASCADE,
        db_column="thematic_surface_id",
        primary_key=True,
    )
    thermalboundary = models.ForeignKey(
        ThermalBoundary, models.CASCADE, db_column="thermalboundary_id"
    )

    class Meta:
        """Metaclass of ThermalBoundaryToThematicSurface."""

        managed = False
        auto_created = True
        db_table = "ng_therm_to_thema_surfa"
        unique_together = (("thematic_surface", "thermalboundary"),)
