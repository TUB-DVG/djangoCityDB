"""Documentation missing."""
from citydb.models import CityModel
from citydb.models import ObjectClass
from citydb.models import EnergyBuilding
from citydb.models import EnergyConversionSystem
from citydb.models import MechanicalVentilation
from citydb.models import ThermalZone
from citydb.models import UsageZone
from citydb.models import Occupants
from citydb.models import Facilities
from citydb.models import ThermalBoundary
from citydb.models import ThermalOpening
from citydb.models import Construction
from citydb.models import TimeSeriesSchedule
from citydb.models import IrregularTimeSeriesFile
from citydb.models import SystemOperation


def get_all_buildings(city_model):
    """Documentation missing."""
    return EnergyBuilding.objects.filter(
        pk__in=city_model.city_object_member.filter(
            objectclass=ObjectClass.objects.get(classname="Building")
        )
        .values("building_obj__building_energy_obj__id")
        .values_list("pk", flat=True)
    )


def get_building_by_name(city_model, name):
    """Documentation missing."""
    return city_model.city_object_member.get(
        objectclass=ObjectClass.objects.get(classname="Building"), name=name
    ).building_obj.building_energy_obj


def get_buildings_by_name(city_model, names):
    """Documentation missing."""
    return EnergyBuilding.objects.filter(
        _parent_link_eb___parent_link__city_model=city_model, name__in=names
    )


def get_all_city_models():
    """Documentation missing."""
    return CityModel.objects.all()


def get_city_model_by_name(name):
    """Documentation missing."""
    return CityModel.objects.get(name=name)


def delete_city_model(name):
    """Documentation missing."""
    cm = CityModel.objects.get(name=name)
    co_to_del = cm.city_object_member.all()
    bldg_to_del = EnergyBuilding.objects.filter(
        id__in=co_to_del.values("building_obj__building_energy_obj__id").values_list(
            "pk", flat=True
        )
    )

    energy_system_to_del = EnergyConversionSystem.objects.filter(
        installed_in__id__in=co_to_del.values_list("pk", flat=True)
    )
    system_operation_to_del = SystemOperation.objects.filter(
        energy_conversion_system__in=energy_system_to_del.values_list("pk", flat=True)
    )
    irr_time_series_to_del = IrregularTimeSeriesFile.objects.filter(
        series_related_to__id__in=system_operation_to_del.values_list("pk", flat=True)
    )
    mechanical_ventilation_to_del = MechanicalVentilation.objects.filter(
        installed_in__id__in=co_to_del.values_list("pk", flat=True)
    )
    system_operation_mech_to_del = SystemOperation.objects.filter(
        energy_conversion_system__in=mechanical_ventilation_to_del.values_list(
            "pk", flat=True
        )
    )
    irr_time_series_mech_to_del = IrregularTimeSeriesFile.objects.filter(
        series_related_to__id__in=system_operation_mech_to_del.values_list(
            "pk", flat=True
        )
    )
    thermal_zones_to_del = ThermalZone.objects.filter(
        building__in=bldg_to_del.values_list("pk", flat=True)
    )
    usage_zones_to_del = UsageZone.objects.filter(
        thermal_zone__in=thermal_zones_to_del.values_list("pk", flat=True)
    )
    occupants_to_del = Occupants.objects.filter(
        usage_zone_occupied_by__in=usage_zones_to_del.values_list("pk", flat=True)
    )
    occupants_to_del = Occupants.objects.filter(
        usage_zone_occupied_by__in=usage_zones_to_del.values_list("pk", flat=True)
    )
    facilities_to_del = Facilities.objects.filter(
        usage_zone_equipped_with__in=usage_zones_to_del.values_list("pk", flat=True)
    )
    thermal_bounds_to_del = ThermalBoundary.objects.filter(
        delimites__in=thermal_zones_to_del.values_list("pk", flat=True)
    )
    thermal_opening_to_del = ThermalOpening.objects.filter(
        thermal_boundary__in=thermal_bounds_to_del.values_list("pk", flat=True)
    )

    construction_tb_to_del = Construction.objects.filter(
        construction_tb__in=thermal_bounds_to_del.values_list("pk", flat=True)
    )
    construction_to_to_del = Construction.objects.filter(
        construction_to__in=thermal_opening_to_del.values_list("pk", flat=True)
    )
    heating_schedule_to_del = TimeSeriesSchedule.objects.filter(
        usagezone_heating__in=usage_zones_to_del.values_list("pk", flat=True)
    )
    cooling_schedule_to_del = TimeSeriesSchedule.objects.filter(
        usagezone_cooling__in=usage_zones_to_del.values_list("pk", flat=True)
    )
    occ_schedule_to_del = TimeSeriesSchedule.objects.filter(
        occupancy_rate__in=occupants_to_del.values_list("pk", flat=True)
    )
    vent_schedule_to_del = TimeSeriesSchedule.objects.filter(
        facilites__in=facilities_to_del.values_list("pk", flat=True)
    )

    heat_time_to_del = IrregularTimeSeriesFile.objects.filter(
        schedule_time_depending_obj__in=heating_schedule_to_del.values_list(
            "pk", flat=True
        ),
        file_id__contains=name,
    )
    cool_time_to_del = IrregularTimeSeriesFile.objects.filter(
        schedule_time_depending_obj__in=cooling_schedule_to_del.values_list(
            "pk", flat=True
        ),
        file_id__contains=name,
    )
    occ_time_to_del = IrregularTimeSeriesFile.objects.filter(
        schedule_time_depending_obj__in=occ_schedule_to_del.values_list(
            "pk", flat=True
        ),
        file_id__contains=name,
    )
    vent_time_to_del = IrregularTimeSeriesFile.objects.filter(
        schedule_time_depending_obj__in=vent_schedule_to_del.values_list(
            "pk", flat=True
        ),
        file_id__contains=name,
    )

    heat_time_to_del.delete()
    cool_time_to_del.delete()
    occ_time_to_del.delete()
    vent_time_to_del.delete()
    construction_to_to_del.delete()
    construction_tb_to_del.delete()
    thermal_bounds_to_del.delete()
    thermal_opening_to_del.delete()
    heating_schedule_to_del.delete()
    cooling_schedule_to_del.delete()
    occ_schedule_to_del.delete()
    vent_schedule_to_del.delete()
    occupants_to_del.delete()
    facilities_to_del.delete()
    usage_zones_to_del.delete()
    thermal_zones_to_del.delete()
    irr_time_series_to_del.delete()
    irr_time_series_mech_to_del.delete()
    system_operation_to_del.delete()
    system_operation_mech_to_del.delete()
    mechanical_ventilation_to_del.delete()
    energy_system_to_del.delete()
    bldg_to_del.delete()
    co_to_del.delete()
    cm.delete()
