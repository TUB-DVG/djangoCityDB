"""This module contains the class Opening from 3DCityDB."""

from citydb.modules.core.cityobject import CityObject
from citydb.modules.core.objectclass import ObjectClass
from citydb.modules.geometry.surface_geometry import SurfaceGeometry
from django.contrib.gis.db import models


class Opening(CityObject):
    """ORM class for opening table from 3DCityDB.

    This is a base class for semantically describing openings
    like doors or windows. The geometric representation of openings only exists
    in models of LoD3 and LoD4. However, this class is base class for
    ThermalOpening from EnergyADE.

    The ForeignKey to ImplicitGeometry, including anchor and reference points
    is not modelled in this context and can be added upon request. The ForeignKey
    to Address is not modelled in this context and can be added upon request.

    The Opening inherits from CityObject, thus all attributes of CityObject
    are directly accessible through Opening.

    Parameters
    ----------
    objectclass_op : ObjectClass
        Foreign key to ObjectClass identifier of this opening.
    lodX_multi_surface : Geometry (tbd)
        LoDX geometry (surface) of the opening, only available in LoD3
        and LoD4.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="opening_obj",
    )
    objectclass_op = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )
    lod3_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="lod3_multi_surface",
    )
    lod4_multi_surface = models.ForeignKey(
        SurfaceGeometry,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="lod4_multi_surface",
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for Opening.

        Since 3D CityDB 4.0.0 every Opening has its own objectclass id. Since
        Django does not allow overwriting inherited fields, we must catch this
        manually.
        """
        super(Opening, self).__init__(*args, **kwargs)
        try:
            self.objectclass_op = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate Opening without passing an ObjectClass."
            )

    class Meta:
        """Metaclass of Opening."""

        managed = False
        db_table = "opening"
