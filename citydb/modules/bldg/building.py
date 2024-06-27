"""This module contains the abstract class Building from 3DCityDB."""

from citydb.modules.core.cityobject import CityObject
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from django.contrib.gis.db import models
from citydb.modules.core.objectclass import ObjectClass


class Building(CityObject):
    """ORM class for building table from 3DCityDB.

    Note: You should not use Building by itself, instead please use
    EnergyBuilding.

    This is the Object-relational mapping class for the SQL building table from
    3DCityDB. As all attributes are defined in the CityGML schema, the
    documentation of these attributes is mostly taken from:
    http://en.wiki.quality.sig3d.org/index.php/Modeling_Guide_for_3D_Objects_-_Part_2:_Modeling_of_Buildings_(LoD1,_LoD2,_LoD3)#Building_.28bldg:Building.29
    However, not all of the description are marked with quotes.

    The building inherits from CityObject, thus all attributes of CityObject
    are directly accessible through Building.

    A building is defined as 'A free-standing self-supporting construction that
    is roofed, usually walled, and can be entered by humans and is normally
    designed to stand permanently in one place. It is intended for human
    occupancy (for example: a place of work or recreation), habitation and/or
    shelter of humans, animals or things.'

    Parameters
    ----------
    objectclass_bld : ObjectClass
        Foreign key to ObjectClass identifier of this building.
    building_parent : Building
        Identifier to another Building instance/entry if this building instance
        is a subbuilding, foreign key in database.
    building_root : Building
        Identifier to another Building instance/entry if this building instance
        is a parent building, foreign key in database.
    class_field : string
        Allows an unspecified classification of the building. In SQL database
        this attribute is called 'class'. If this attribute is used, you need
        to make sure that the classification is documented (class_codespace)
        and consistent throughout the whole project.
    class_codespace : string
        Describes the classification of the used class methodology. Should be
        used if attribute 'class_field' ist used.
    function : string
        The function of a building is the predominantly functional significance
        of the building at the date of data collection.
    function_codespace : string
        Describes the used methodology for function.
    usage : string
        The usage of a building describes the use of the building and contains
        the respective percentage usage share of the total use.
    usage_codespace: string
        Describes the used methodology for usage.
    year_of_construction : date
        The year of construction is the year of completion of the construction
        or alteration of the building.
    year_of_demolition : date
        The year of demolition is the year of deconstruction of the building.
    roof_type : string
        The roof type describes the characteristic shape of the roof.
    roof_type_codespace : string
        Describes the used methodology for roof_type.
    measured_height : float [m]
        The measured height is the difference in [m] between the highest point
        of the roof structure and the defined footprint of the building.
    measured_height_unit : string
        Defines the unit of measurement of measured_height, should always
        be [m].
    storeys_above_ground : integer
        Storeys above ground is the number of floors above ground level.
    storeys_below_ground : integer
        Storeys below ground is the number of floors below ground level
        (cellar).
    storey_heights_above_ground : float
        Height between two consecutive floors of the above-ground floors.
    storey_heights_ag_unit : string
        Defines the unit of measurement of storey_heights_above_ground, should
        always be [m].
    storey_heights_below_ground : float
        Height between two consecutive floors of the underground floors.
    storey_heights_bg_unit : string
        Defines the unit of measurement of storey_heights_below_ground, should
        always be [m].
    lodX__terrain_intersection : Geometry (tbd)
        LoDX geometry (curve) of the terrain intersection line of the building
    lodX_multi_curve : Geometry (tbd)
        LoDX geometry (curve) of the building (usage not recommended).
    lod0_footprint : SurfaceGeometry
        Footprint geometry of the building (only LoD 0).
    lod0_roofprint : SurfaceGeometry
        Roofprint geometry of the building (only LoD 0).
    lodX_multi_surface : SurfaceGeometry
        LoDX geometry (surface) of the building (usage not recommended).
    lodX_solid : SurfaceGeometry
        LoDX geometry (volume)of the building.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="building_obj",
    )
    objectclass_bld = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )
    building_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="parent_id",
    )
    building_root = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="root_id"
    )
    # Field renamed because it was a Python reserved word.
    class_field = models.CharField(
        db_column="class", max_length=256, blank=True, null=True
    )
    class_codespace = models.CharField(max_length=4000, blank=True, null=True)
    function = models.CharField(max_length=1000, blank=True, null=True)
    function_codespace = models.CharField(max_length=4000, blank=True, null=True)
    usage = models.CharField(max_length=1000, blank=True, null=True)
    usage_codespace = models.CharField(max_length=4000, blank=True, null=True)
    year_of_construction = models.DateField(blank=True, null=True)
    year_of_demolition = models.DateField(blank=True, null=True)
    roof_type = models.CharField(max_length=256, blank=True, null=True)
    roof_type_codespace = models.CharField(max_length=4000, blank=True, null=True)
    measured_height = models.FloatField(blank=True, null=True)
    measured_height_unit = models.CharField(max_length=4000, blank=True, null=True)
    storeys_above_ground = models.IntegerField(blank=True, null=True)
    storeys_below_ground = models.IntegerField(blank=True, null=True)
    storey_heights_above_ground = models.FloatField(blank=True, null=True)
    storey_heights_ag_unit = models.CharField(max_length=4000, blank=True, null=True)
    storey_heights_below_ground = models.CharField(
        max_length=4000, blank=True, null=True
    )
    storey_heights_bg_unit = models.CharField(max_length=4000, blank=True, null=True)
    lod1_terrain_intersection = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod2_terrain_intersection = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod3_terrain_intersection = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod4_terrain_intersection = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod2_multi_curve = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod3_multi_curve = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod4_multi_curve = models.MultiLineStringField(
        dim=3, srid=25832, blank=True, null=True
    )
    lod0_footprint = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod0_foot_id",
    )
    lod0_roofprint = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod0_root_id",
    )
    lod1_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod1_multi_id",
    )
    lod2_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod2_multi_id",
    )
    lod3_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod3_multi_bldg",
    )
    lod4_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod4_multi_bldg",
    )
    lod1_solid = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod1_solid_bldg",
    )
    lod2_solid = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod2_solid_bldg",
    )
    lod3_solid = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod3_solid_bldg",
    )
    lod4_solid = models.ForeignKey(
        SurfaceGeometry,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lod4_solid_bldg",
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for buildings.

        Since 3D CityDB 4.0.0 every building has its own objectclass id. Since
        Django does not allow overwriting inherited fields, we must catch this
        manually.
        """
        super(Building, self).__init__(*args, **kwargs)
        try:
            self.objectclass_bld = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate Building without passing an "
                "ObjectClass"
            )

    class Meta:
        """Metaclass of Building."""

        managed = False
        abstract = False
        db_table = "building"
