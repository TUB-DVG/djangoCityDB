"""This module contains the classes AbstractEnergySystem, EnergySystemToCityObject and
EnergyConversionSystem from EnergyADE."""

from citydb.modules.core.cityobject import CityObject
from django.contrib.gis.db import models
from citydb.modules.core.objectclass import ObjectClass
from citydb.modules.energy.core.servicelife import ServiceLife


class AbstractEnergySystem(CityObject):
    """Abstract ORM class for energy systems from EnergyADE.

    The AbstractEnergySystem inherits from CityObject, thus all attributes of
    CityObject are directly accessible through AbstractEnergySystem.

    Note: Please do not use this class, but instead the inherited classes.

    Parameters
    ----------
    model : string
        Producer specific name of the energy system.
    number_of_devices : integer
        ***Description missing.***
    objectclass_system : ObjectClass
        ***Description missing.***
    service_life : ServiceLife
        Foreign key to the corresponding ServiceLife instance.
    year_of_manufacture: date
        Year of manufacture (which is assumed to be the year of installation).
    installed_in : CityObject
        A energy conversion system may be installed in every CityObject.

    """

    _parent_link = models.OneToOneField(
        CityObject,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="_abstract_energy_system_obj",
    )
    model = models.CharField(max_length=1000, blank=True, null=True)
    number_of_devices = models.IntegerField(
        blank=True, null=True, db_column="numberofdevices"
    )
    objectclass_system = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE, default=10012
    )
    service_life = models.ForeignKey(
        ServiceLife,
        models.CASCADE,
        db_column="servicelife_id",
        blank=True,
        null=True,
        related_name="energy_system_service_life",
    )
    year_of_manufacture = models.DateField(
        blank=True, null=True, db_column="yearofmanufacure"
    )
    installed_in = models.ManyToManyField(
        CityObject, through="EnergySystemToCityObject", related_name="energy_system"
    )
    provides = models.ManyToManyField(
        CityObject, 
        blank=True, 
        related_name="provided_by",
        db_column="provides",
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgeign key for AbstractEnergySystem.

        Since 3D CityDB 4.0.0 every AbstractEnergySystem has its own objectclass id.
        Since Django does not allow overwriting inherited fields, we must catch
        this manually.
        """
        super(AbstractEnergySystem, self).__init__(*args, **kwargs)
        try:
            self.objectclass_system = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate AbstractEnergySystem without passing "
                "an ObjectClass"
            )

    class Meta:
        """Metaclass for AbstractEnergySystem."""

        managed = False
        db_table = "ng_energysystem"


class EnergySystemToCityObject(models.Model):
    """A mapping table to manage the relations of energy systmes and city objects.

    This is an internal class that is not meant for manual manipulations.
    Active use is therefore not recommended.
    """

    city_object = models.ForeignKey(
        CityObject, models.CASCADE, primary_key=True, db_column="cityobject_id"
    )
    energy_system = models.ForeignKey(
        AbstractEnergySystem,
        models.CASCADE,
        primary_key=True,
        db_column="energysystem_id",
    )

    class Meta:
        """Metaclass for EnergySystemToCityObject."""

        managed = False
        auto_created = True
        db_table = "ng_energysy_to_cityobje"
        unique_together = (("city_object", "energy_system"),)


class EnergyConversionSystem(AbstractEnergySystem):
    """ORM class for energy_conversion_system table from EnergyADE.

    General EnergyConversionSystem which is not specified in a more detailed way.

    Inherits from AbstractEnergySystem.

    Parameters
    ----------
    efficiency_indicator : string
        Reference efficiency ratio used to quantify the system efficiency (e.g. COP,
        EER, W/(m3/h)).
    has_condensation : float
        ***Description missing.***
    installed_power : float [***]
        Total nominal power of the energy conversion system.
    installed_power_uom : string
        Defines the unit of measurement of installed_power, should always be [***].
    nominal_efficiency : float
        Nominal efficiency of the energy conversion system.
    nominal_efficiency_uom : string
        Defines the unit of measurement of nominal_efficiency.
    objectclass_conv_system : ObjectClass
        ***Description missing.***

    """

    _abst_conv_sys = models.OneToOneField(
        AbstractEnergySystem,
        on_delete=models.CASCADE,
        db_column="id",
        primary_key=True,
        parent_link=True,
        default=None,
        related_name="energy_conversion_system_obj",
    )
    efficiency_indicator = models.CharField(
        max_length=1000, blank=True, null=True, db_column="efficiencyindicator"
    )
    has_condensation = models.FloatField(
        blank=True, null=True, db_column="hascondensation"
    )
    installed_power = models.FloatField(
        blank=True, null=True, db_column="installedpower"
    )
    installed_power_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="installedpower_uom"
    )
    nominal_efficiency = models.FloatField(
        blank=True, null=True, db_column="nominalefficiency"
    )
    nominal_efficiency_uom = models.CharField(
        max_length=1000, blank=True, null=True, db_column="nominalefficiency_uom"
    )
    objectclass_conv_system = models.ForeignKey(
        ObjectClass, db_column="objectclass_id", on_delete=models.CASCADE
    )

    def __init__(self, *args, **kwargs):
        """Catch ObjectClass Forgein key for EnergyConversionSystem.

        Since 3D CityDB 4.0.0 every EnergyConversionSystem has its own
        objectclass id. Since Django does not allow overwriting inherited fields, we
        must catch this manually.
        """
        super(EnergyConversionSystem, self).__init__(*args, **kwargs)
        try:
            self.objectclass_conv_system = self.objectclass
        except ObjectClass.DoesNotExist:
            raise ObjectClass.DoesNotExist(
                "You should never instantiate EnergyConversionSystem without passing "
                "an ObjectClass"
            )

    class Meta:
        """Metaclass of EnergyConversionSystem."""

        managed = False
        db_table = "ng_energyconversionsyst"
