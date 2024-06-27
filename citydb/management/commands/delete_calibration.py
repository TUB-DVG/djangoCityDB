from django.core.management.base import BaseCommand, CommandError
import citydb.shortcuts.buildings_data as bd_short
from citydb.models import CityModel
from calibration.models import BayesianCalibration
from calibration.models import BuildingMapping
from calibration.models import SensitivityAnalysis
from calibration.models import GaussianProcess
from calibration.models import Emulator


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("city_model_name", nargs="+", type=str)

    def handle(self, *args, **options):

        for cm_name in options["city_model_name"]:

            try:
                BuildingMapping.objects.filter(name__contains=cm_name).delete()
            except BayesianCalibration.DoesNotExist:
                pass
            try:
                BayesianCalibration.objects.filter(name__contains=cm_name).delete()
            except BayesianCalibration.DoesNotExist:
                pass
            try:
                SensitivityAnalysis.objects.filter(name__contains=cm_name).delete()
            except SensitivityAnalysis.DoesNotExist:
                pass
            try:
                GaussianProcess.objects.filter(name__contains=cm_name).delete()
            except GaussianProcess.DoesNotExist:
                pass
            try:
                Emulator.objects.filter(name__contains=cm_name).delete()
            except Emulator.DoesNotExist:
                pass
            try:
                all_cm = CityModel.objects.filter(name__contains=cm_name)
                for name in all_cm:
                    bd_short.delete_city_model(name=name.gmlid)
            except CityModel.DoesNotExist:
                raise CommandError('CityModel "%s" does not exist' % cm_name)
            self.stdout.write(
                self.style.SUCCESS('Successfully deleted CityModel "%s"' % cm_name)
            )
