"""Attention: running this script will delete all data in your databses

Run this with `python manage.py flush_db` to delete all data from your DB. If
you want to omit being asked to confirm the deleting, use
`python manage.py flush_db --force`.
"""

from django.core.management.base import BaseCommand

from citydb.models import CityModel
from citydb.models import CityObject
from citydb.models import ObjectClass


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force flushing without being asked for confirmation",
        )

    def _flush_db(self, force=False):
        if force:
            response = "y"
        else:
            response = input(
                "\n"
                "!!!WARNING!!! \n"
                "This will delete all data of 3DCityDB citydb app in your database, except the classes SolidMaterial and IrregularTimeSeriesFile, which is intended behaviour."
                "Are you sure you would like to delete all data? (y/[n]): "
                or "n"
            )
            if not response:
                response = "n"

        if response == "y":
            print("Start deleting data...")

            CityObject.objects.all().exclude(
                objectclass=ObjectClass.objects.get(classname="SolidMaterial")
            ).exclude(
                objectclass=ObjectClass.objects.get(classname="IrregularTimeSeriesFile")
            ).delete()
            # CityObject.objects.all().delete()
            CityModel.objects.all().delete()
            print("All data deleted...")

    def handle(self, *args, **options):
        self._flush_db(options["force"])
