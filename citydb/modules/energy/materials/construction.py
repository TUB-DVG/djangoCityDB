"""This module contains the super class AbstractConstruction and the derived class Construction from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.core.cityobject import CityObject
from citydb.modules.energy.core.energybuilding import EnergyBuilding
from citydb.modules.energy.materials.opticalproperties import OpticalProperties
from citydb.modules.energy.core.servicelife import ServiceLife


class AbstractConstruction(CityObject):
    """Abstract ORM class for construction from EnergyADE.

    Abstract super class of Construction.

    Parameters:
    -----------
    base_construction : AbstractConstruction
        ***Description missing.***
    building : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="_abstract_construction_obj",
    )
    base_construction = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column="baseconstruction_id",
    )
    building = models.ForeignKey(
        EnergyBuilding,
        db_column="building_aggregatedbuildi_id",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="building_construction",
    )

    class Meta:
        """Metaclass of AbstractConstruction."""

        managed = False
        db_table = "ng_construction"


class Construction(AbstractConstruction):
    """ORM class for construction table from EnergyADE.

    Holds (wall-)construction details.

    Parameters:
    -----------
    optical_properties : OpticalProperties
        Optical properties of a Construction.
    service_life : ServiceLife
        Information of product life time and maintenance intervals.
    u_value : float [W/m²K]
        Overall heat transfer coefficient. It represents the heat flux transfer through
        a construction, normalized by the construction surface and the difference of
        temperature across the construction, at steady state.
    u_value_uom : string
        Defines the unit of measurement of u_value, should always be [W/m²K].

    """

    _abst_const = models.OneToOneField(
        AbstractConstruction,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="construction_obj",
    )
    optical_properties = models.ForeignKey(
        OpticalProperties,
        models.CASCADE,
        db_column="opticalproperties_id",
        blank=True,
        null=True,
        related_name="construction_opt_prop",
    )
    service_life = models.ForeignKey(
        ServiceLife,
        models.CASCADE,
        db_column="servicelife_id",
        blank=True,
        null=True,
        related_name="construction_service_life",
    )
    u_value = models.FloatField(db_column="uvalue", blank=True, null=True)
    u_value_uom = models.CharField(
        db_column="uvalue_uom", max_length=1000, blank=True, null=True
    )

    class Meta:
        """Metaclass of Construction."""

        managed = False
        db_table = "ng_construction_1"
