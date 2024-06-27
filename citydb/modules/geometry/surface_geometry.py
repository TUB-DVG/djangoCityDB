"""This module contains the class SurfaceGeometry from 3DCityDB."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models


class SurfaceGeometry(models.Model):
    """ORM class for surface_geometry table from 3DCityDB.

    The surface geometry can store polygonal geometry and 3D geometries.

    Note: the 3DCityDB field solid_geometry is not supported in our framework,
    the reason for this is the unssuported field type PolyhedralSurfaceZ in
    GeoDjango.

    For detailed description of SurfaceGeometry we'd like to refer to https://
    www.3dcitydb.org/3dcitydb/fileadmin/downloaddata/3DCityDB_Documentation_v3.pdf page
    55ff

    Parameters
    ----------
    gmlid : string
        Unique identifier of CityGML surface geometry.
    gmlid_codespace : string
        As it cannot be guarenteed that the gmlid is unique over different
        projects you can specify the codespace.
    parent : SurfaceGeometry
        Foreign key to same table if 3D data is used (connect multiple polygons
        geometrically).
    root : SurfaceGeometry
        Foreign key to same table if 3D data is used (connect multiple polygons
        geometrically)
    is_solid : float
        Flag to characterise type of aggregation, the field of 3DCityDB is
        numeric, however only 0 (surface) or 1 (solid) are allowed.
    is_composite : float
        Flag to characterise type of aggregation, the field of 3DCityDB is
        numeric, however only 0 (MultiSolid) or 1 (CompositeSolid) are allowed.
    is_triangulated : float
        Flag to characterise type of aggregation, the field of 3DCityDB is
        numeric, however only 0 (isTriangulated) or 1 (isNotTriangulated) are
        allowed.
    is_xlink : float
        Allows sharing of geometry objects between different. Again 3DCityDB
        fiel type is numeric.
    is_reverse : float
        0 for no reverse, 1 if the exporter should reverse this geometry.
    geometry : GeometryField
        3 dimensional geometry field, use this field for you geometry.
    implicit_geometry : GeometryField
        3 dimensional geometry field, use this for reusable geometries (e.g.
        vegetation), implicit_geometry has no srid information.
    cityobject : CityObect
        Foreign key to a CityObject this surface belongs to (e.g. directly a
        Building or a ThematicSurface).

    """

    gmlid = models.CharField(max_length=256, blank=True, null=True)
    gmlid_codespace = models.CharField(max_length=1000, blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="surface_parent",
    )
    root = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="surface_root",
    )
    is_solid = models.FloatField(blank=True, null=True)
    is_composite = models.FloatField(blank=True, null=True)
    is_triangulated = models.FloatField(blank=True, null=True)
    is_xlink = models.FloatField(blank=True, null=True)
    is_reverse = models.FloatField(blank=True, null=True)
    # solid_geometry = models.GeometryField(
    #     srid=25832,
    #     blank=True,
    #     null=True)
    geometry = models.GeometryField(srid=25832, blank=True, null=True)
    implicit_geometry = models.PolygonField(dim=3, blank=True, null=True)
    cityobject = models.ForeignKey(
        CityObject,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="thematic_surface_geom",
    )

    def __str__(self):
        """Override __str__method."""
        return "SurfaceGeometry {}".format(self.id)

    class Meta:
        """Metaclass of SurfaceGeometry."""

        managed = False
        db_table = "surface_geometry"
