"""This module contains the class EnergyPerformanceCertificate from EnergyADE."""

from citydb.modules.energy.core.energybuilding import EnergyBuilding
from django.contrib.gis.db import models
from citydb.modules.energy.occupants.buildingunit import BuildingUnit


class EnergyPerformanceCertificate(models.Model):
    """ORM class for energy_performance_certificate table from EnergyADE.

    Energy performance certification.

    Parameters
    ----------
    building_performancecert : EnergyBuilding
        Foreign key to the corresponding EnergyBuilding instance.
    buildingunit_performancecert : BuildingUnit
        Foreign key to the corresponding BuildingUnit instance.
    certificationid : string
        Identifier of the energy certificate.
    name : string
        Labeling system for the energy certificate.
    rating : string
        Degree or value resulting from the certification assessment.

    """

    building_performancecert = models.ForeignKey(
        EnergyBuilding,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="building_energyperformanc_id",
        related_name="energy_performance_certification_bldg",
    )
    buildingunit_performancecert = models.ForeignKey(
        BuildingUnit,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="energy_performance_certification_bldg_unit",
        db_column="buildingunit_energyperfor_id",
    )
    certificationid = models.CharField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=1000, blank=True, null=True)
    rating = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        """Metaclass of EnergyPerformanceCertificate."""

        managed = False

        db_table = "ng_energyperformancecer"
