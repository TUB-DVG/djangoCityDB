from django.core.management.base import BaseCommand, CommandError
import citydb.shortcuts.buildings_data as bd_short
from citydb.models import CityModel


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("city_model_name", nargs="+", type=str)

    def handle(self, *args, **options):

        for cm_name in options["city_model_name"]:
            try:
                bd_short.delete_city_model(name=cm_name)
            except CityModel.DoesNotExist:
                raise CommandError('CityModel "%s" does not exist' % cm_name)

            self.stdout.write(
                self.style.SUCCESS('Successfully deleted CityModel "%s"' % cm_name)
            )
