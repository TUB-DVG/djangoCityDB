"""This module contains the class SurfaceGeometry from 3DCityDB."""

from citydb.modules.core.cityobject import CityObject
from citydb.modules.core.objectclass import ObjectClass
from citydb.modules.bldg.building import Building
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from django.contrib.gis.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


class ThematicSurface(CityObject):
    """ORM class for thematic_geometry table from 3DCityDB.

    The ThematicSurface inherits from CityObject, thus all attributes of
    CityObject are directly accessible through ThematicSurface.

    The Thematic surface connects MultiPolygon and their corresponding
    objectclass.

    Parameters
    ----------
    building : Building
        Foreign key relationship to the building.
    lodX_multi_surface : SurfaceGeometry
        Foreign key to LoDX geometry (surface) (usage not recommended).

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="thematicsurface_obj",
    )
    objectclass_ts = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )
    building = models.ForeignKey(
        Building,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="bldg_thematic_surface",
    )
    lod2_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="thematic_surface_lod2",
    )
    lod3_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="thematic_surface_lod3",
    )
    lod4_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="thematic_surface_lod4",
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for thematic surface.

        Since 3D CityDB 4.0.0 every ThematicSurface has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        super(ThematicSurface, self).__init__(*args, **kwargs)
        try:
            self.objectclass_ts = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate ThematicSurface without passing "
                "an ObjectClass"
            )

    def __str__(self):
        """Return id of ThematicSurface."""
        return "ThematicSurface {}".format(self.id)

    class Meta:
        """Metaclass of ThematicSurface."""

        managed = False
        db_table = "thematic_surface"


@receiver(post_delete, sender=ThematicSurface, dispatch_uid="delete_co")
def auto_delete_cityobject(sender, instance, **kwargs):
    """Patch to delete also CityObject of ThematicSurface."""
    try:
        sg = SurfaceGeometry.objects.get(cityobject=instance._parent_link)
        sg.cityobject = None
        sg.save()
        bldg = Building.objects.get(lod2_solid=sg)
        bldg.lod0_footprint = None
        bldg.lod0_roofprint = None
        bldg.lod1_multi_surface = None
        bldg.lod2_multi_surface = None
        bldg.lod3_multi_surface = None
        bldg.lod4_multi_surface = None
        bldg.lod1_solid = None
        bldg.lod2_solid = None
        bldg.lod3_solid = None
        bldg.lod4_solid = None
        bldg.save()
    except SurfaceGeometry.DoesNotExist:
        pass
