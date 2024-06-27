import json

from django.core.management.base import BaseCommand

from citydb.models import (
    EnergyDemand,
)

class Command(BaseCommand):
    help = 'Read timeseries from the CityDB.'

    def add_arguments(self, parser):
        # Add any command line arguments here
        parser.add_argument('typeOfTimeSeries', type=str)
        parser.add_argument('buildingID', type=str)
        parser.add_argument("--end_use" , type=str, help="End use of the energy demand.")

    def handle(self, *args, **options):
        # Your command logic goes here
        

        if options['typeOfTimeSeries'] == 'EnergyDemand':
            if options['end_use']:
                return self._readEnergyDemand(options['buildingID'], options['end_use'])
            else:
                return self._readEnergyDemand(options['buildingID'])
        else:
            ValueError('Reading the specified timeseries is not supported yet.')
        
    def _createArrayOfTimings(self, timeSeries):
        """

        """
        timeSeriesArray = []
        numberOfElements = len(timeSeries.values.split(" "))
        startDatetime = timeSeries.timeperiodprop_beginposition
        endDatetime = timeSeries.timeperiodproper_endposition
        for i in range(numberOfElements):
            currentDateTime = startDatetime + i * (endDatetime - startDatetime) / numberOfElements
            timeSeriesArray.append(str(currentDateTime))

        return timeSeriesArray


    def _readEnergyDemand(self, buildingID, end_use=None):
        """

        """
        energyDemandDict = {}
        if end_use:
            energyDemandForBuilding = EnergyDemand.objects.filter(cityObjectDemandsID__id__gmlid=buildingID, end_use=end_use)
        else:
            energyDemandForBuilding = EnergyDemand.objects.filter(cityObjectDemandsID__id__gmlid=buildingID)

        for energyDemand in energyDemandForBuilding:
            if energyDemand.energy_amount is not None:
                timeSeriesForDemand = energyDemand.energy_amount.regular_time_series
                energyDemandDict[f"{energyDemand.end_use}_{timeSeriesForDemand.values_uom}"] = {}
                energyDemandDict[f"{energyDemand.end_use}_{timeSeriesForDemand.values_uom}"]["time"] = self._createArrayOfTimings(timeSeriesForDemand)
                energyDemandDict[f"{energyDemand.end_use}_{timeSeriesForDemand.values_uom}"]["data"] = [float(strElement) for strElement in timeSeriesForDemand.values.split(" ")]
        stringifiedOutput = json.dumps(energyDemandDict)
        return stringifiedOutput

