"""This module contains the super class AbstractMaterial and the derived classes Gas and SolidMaterial from EnergyADE."""
from django.contrib.gis.db import models
from citydb.modules.core.cityobject import CityObject
from citydb.modules.core.objectclass import ObjectClass


class AbstractMaterial(CityObject):
    """Abstract ORM class for material from EnergyADE.

    Abstract super class of Gas and SolidMaterial.

    Parameters:
    -----------
    objectclass_mat : ObjectClass
        Foreign key to the corresponding ObjectClass instance.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="_abstract_material_obj",
    )

    objectclass_mat = models.ForeignKey(
        ObjectClass,
        db_column="objectclass_id",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for thematic surface.

        Since 3D CityDB 4.0.0 every AbstractMaterial has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        super(AbstractMaterial, self).__init__(*args, **kwargs)
        try:
            self.objectclass_mat = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate AbstractMaterial without passing "
                "an ObjectClass"
            )

    class Meta:
        """Metaclass of AbstractMaterial."""

        managed = False
        db_table = "ng_material"


class Gas(AbstractMaterial):
    """ORM class for gas table from EnergyADE.

    Holds details for a gaseous material.

    Parameters:
    -----------
    is_ventilated : float
        Value is 1 if the gas-layer is ventilated, else 0.
    r_value : float [K*m/W]
        Specific thermal Resistance of the material.
    r_value_uom : string
        Defines the unit of measurement of r_value, should always be [K*m/W].

    """

    _abst_material = models.OneToOneField(
        AbstractMaterial,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="gas_abstract",
    )
    is_ventilated = models.FloatField(db_column="isventilated", blank=True, null=True)
    r_value = models.FloatField(db_column="rvalue", blank=True, null=True)
    r_value_uom = models.CharField(
        db_column="rvalue_uom", max_length=1000, blank=True, null=True
    )

    class Meta:
        """Metaclass of Gas."""

        managed = False
        db_table = "ng_gas"


class SolidMaterial(AbstractMaterial):
    """ORM class for solid_material table from EnergyADE.

    Holds details for a solid material.

    Parameters:
    -----------
    conductivity : float [W/(m*K)]
        Thermal conductivity of the material.
    conductivity_uom : string
        Defines the unit of measurement of conductivity, should always be [W/(m*K)].
    density : float [kg/m³]
        Density of the material.
    density_uom : string
        Defines the unit of measurement of density, should always be [kg/m³].
    embodied_carbon : float
        CO2 equivalent emissions caused by the fabrication and transportation on site
        of the material.
    embodied_carbon_uom : string
        Defines the unit of measurement of embodied_carbon, should be kg of CO2 per m³
        or kg of CO2 per kg material.
    embodied_energy : float
        Primary energy consumed for the fabrication and transportation on site of the
        material.
    embodied_energy_uom : string
        Defines the unit of measurement of embodied_energy, should be Joule per m³ or
        Joule per kg material.
    permeance : float [***]
         Water vapor transmission rate through the material.
    permeance_uom : string
        Defines the unit of measurement of permeance, should always be [***] (g*m²*mmHG/
        24h?).
    porosity : float
        Ratio of the total amount of void space in a material (due to poses, small
        channels, and so on) to the bulk volume occupied by the material, must be
        between 0 and 1.
    porosity_uom : string
        Defines the unit of measurement of porosity.
    specific_heat : float [J/(kg*K)]
        Specific heat capacity of the material.
    specific_heat_uom : string
        Defines the unit of measurement of specific_heat, should always be [J/(kg*K)].

    """

    _abst_material = models.OneToOneField(
        AbstractMaterial,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="solid_material_abstract",
    )
    conductivity = models.FloatField(blank=True, null=True)
    conductivity_uom = models.CharField(max_length=1000, blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    density_uom = models.CharField(max_length=1000, blank=True, null=True)
    embodied_carbon = models.FloatField(
        db_column="embodiedcarbon", blank=True, null=True
    )
    embodied_carbon_uom = models.CharField(
        db_column="embodiedcarbon_uom", max_length=1000, blank=True, null=True
    )
    embodied_energy = models.FloatField(
        db_column="embodiedenergy", blank=True, null=True
    )
    embodied_energy_uom = models.CharField(
        db_column="embodiedenergy_uom", max_length=1000, blank=True, null=True
    )
    permeance = models.FloatField(blank=True, null=True)
    permeance_uom = models.CharField(max_length=1000, blank=True, null=True)
    porosity = models.FloatField(blank=True, null=True)
    porosity_uom = models.CharField(max_length=1000, blank=True, null=True)
    specific_heat = models.FloatField(db_column="specificheat", blank=True, null=True)
    specific_heat_uom = models.CharField(
        db_column="specificheat_uom", max_length=1000, blank=True, null=True
    )

    class Meta:
        """Metaclass of SolidMaterial."""

        managed = False
        db_table = "ng_solidmaterial"
