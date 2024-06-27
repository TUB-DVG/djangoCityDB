import csv
from datetime import (
    datetime,
    timedelta,
)
import json
import uuid

from django.core.management import BaseCommand
from django.db import models

from citydb.models import (
    CityObject,
    EnergyDemand,
    ObjectClass,
    NgCityObject,
    RegularTimeSeries,
    TimeSeries,
)

class Command(BaseCommand):
    """

    Attributes
    ----------
    LIST_OF_ENERGYDEMAND_ENDUSES : list
        A list with the end-uses of the energy demand.
    LIST_OF_SCHEDDULES : list
        A list with the schedules.
    TIMEPERIODPROP_BEGINPOSITION: DateTime 
        Global start of the time series. That value can differ from the start 
        of the time series inside the schedule, since the time data has been 
        split up in weekDay and weekEnd.
    TIMEPERIODPROPER_ENDPOSITION: DateTime 
        Global end of the time series. That value can differ from the start 
        of the time series inside the schedule, since the time data has been 
        split up in weekDay and weekEnd.
    """
    help = 'Load a csv file into the database'

    LIST_OF_ENERGYDEMAND_ENDUSES = [
        "domesticHotWater",
        "electricalAppliances",
        "lighting",
        "otherOrCombinationElectrical",
        "otherOrCombinationHeating",
        "otherOrCombinationCooling",
        "spaceCooling",
        "spaceHeating",
        "ventilation",
        "ventilationHeating",
        "ventilationCooling",
        "process",
    ]

    def __init__(self):
        """Constructor of the Command class.

        """
        self.TIMEPERIODPROP_BEGINPOSITION = None
        self.TIMEPERIODPROPER_ENDPOSITION = None

    def add_arguments(self, parser):
        parser.add_argument("input", type=str)
        parser.add_argument("buildingID", type=str, help="The ID of the building to which the time series belongs to.")
        parser.add_argument("--acquisition_method", default="simulation", type=str, help="Add a aquistion-method for the TimeSeries.")
        parser.add_argument("--interpolation_type", default="averageInSucceedingInterval", type=str, help="Add a interpolation type for the timeseries")
        parser.add_argument("--quality_description", default="add qualit description here", type=str, help="Add a quality description for the timeseries")
        parser.add_argument("--source", default="EnergyPlus", type=str, help="The type of the demand. For example 'electricity' or 'heat'.")
        parser.add_argument("--thematic_description", default="Heating energy", type=str, help="The type of the demand. For example 'electricity' or 'heat'.")

    def _timeProcessing(self, dictOfTimeSeries: dict) -> tuple:
        """Do the time processing for the time series.

        This method transforms datetime-strings inside the input dict into datetime-objects.
        Furthermore a categorization of the data is done into weekday and weekend data.

        Parameters
        ----------
        dictOfTimeSeries: dict
            A dictionary with the time series data.
        
        Returns
        -------
        tuple
            returns list of datetime-objects and the last time difference.
        """
        datetimeObjList = []
        lastTimeDifference = None
        
        for index, datetimeStr in enumerate(dictOfTimeSeries['DATE']):
            datetimeObj = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S')
            datetimeObjList.append(datetimeObj)

            if index > 0:
                timeDifference = datetimeObj - datetimeObjList[index-1]
                if lastTimeDifference is not None:
                    if timeDifference != lastTimeDifference:
                        print("The time differences in the time series are not equal.")
                lastTimeDifference = timeDifference

        self.TIMEPERIODPROP_BEGINPOSITION = datetimeObjList[0]
        self.TIMEPERIODPROPER_ENDPOSITION = datetimeObjList[-1]

        return datetimeObjList, lastTimeDifference

    def _parseDict(self, dictOfTimeSeries) -> dict:
        """Called, when option["input"] is a dictionary.

        This Test parses the dictionary and returns the time- and data-information, 
        which can then be imported into the database.
        """
        
        dictOfCategorizedKeys = list(dictOfTimeSeries.keys())
        dictOfCategorizedKeys.pop(dictOfCategorizedKeys.index("DATE"))

        datetimeObjList, lastTimeDifference = self._timeProcessing(dictOfTimeSeries)

        # get the timedelta in hours:
        timeDifferenceInHours = lastTimeDifference.total_seconds() / 3600

        dictForDatabase = {}
        dictForDatabase["RegularTimeSeries"] = []
        dictForDatabase["EnergyDemand"] = []
        for key in dictOfCategorizedKeys:
            dataUnit = key.split("_")[1]
            dictForDatabase["RegularTimeSeries"].append(
                {
                    "values": " ".join(map(str, dictOfTimeSeries[key])),
                    "values_uom": dataUnit,
                    "timeperiodprop_beginposition": datetimeObjList[0],
                    "timeperiodproper_endposition": datetimeObjList[-1],
                    "timeinterval_unit": "hour",
                    "timeinterval": timeDifferenceInHours,
                    "timeinterval_factor": 1,
                    "timeinterval_radix": 1,
                }
            )
            dictForDatabase["EnergyDemand"].append(
                {
                "end_use": key.split("_")[0],
                }
            )
        return dictForDatabase
    
    def _updateDjangoObjectFromDict(self, djangoObject: models.Model, dictForUpdate: dict) -> None:
        """Update a Django object with values from a dictionary.

        Parameters
        ----------
        djangoObject: django.db.models.Model
            A Django object.
        dictForUpdate: dict
            Holds as keys the names of the attributes and as values the new values.
        
        Returns
        -------
        None

        """
        for key, value in dictForUpdate.items():
            setattr(djangoObject, key, value)
        djangoObject.save()


    def _createOrUpdateRegularTimeSeries(self, regularTimeSeriesDict, regularTimeSeriesObj=None) -> RegularTimeSeries:
        """Create or update a RegularTimeSeries object.

        If no RegularTimeSeries object is passed, a new one is created. Otherwise the existing
        is updated with the values from `regularTimeSeriesDict`.

        Parameters
        ----------
        regularTimeSeriesDict: dict
            A dictionary with the values for the RegularTimeSeries object.
        regularTimeSeriesObj: RegularTimeSeries
            A RegularTimeSeries object. If None, a new object is created.
        
        Returns
        -------
        RegularTimeSeries
            The RegularTimeSeries object which was created or updated.
        """
        if regularTimeSeriesObj is None:
            
            regularTimeSeriesObjectClass = ObjectClass.objects.get(id=50033)
            newRegularTimeSeries = RegularTimeSeries.objects.create(
                objectclass=regularTimeSeriesObjectClass,
                **regularTimeSeriesDict,
            )
            return newRegularTimeSeries
        else:
            self._updateDjangoObjectFromDict(regularTimeSeriesObj, regularTimeSeriesDict)
            return regularTimeSeriesObj


    def _writeEnergyDemandIntoDatabase(self, dictForDatabase, options) -> None:
        """Writes the values of the dictionary `dictForDatabase` into the database.

        `dictForDatabase` is a nested dictionary. In the first layer the keys are
        the names of the CityDB-Tables. The values are dictionaries whereby the keys
        are the names of the corresponding attributes.
        
        """
        buildingID = options.pop("buildingID", None)
        for index, energyDemandInputValue in enumerate(dictForDatabase["EnergyDemand"]):
            energyDemandQuerySetForBuilding = EnergyDemand.objects.filter(cityObjectDemandsID__id__gmlid=buildingID, end_use=energyDemandInputValue["end_use"])
            if energyDemandQuerySetForBuilding.exists() and energyDemandQuerySetForBuilding[0].energy_amount is not None:
                regularTimeSeriesUpdatedOrCreated = self._createOrUpdateRegularTimeSeries(dictForDatabase["RegularTimeSeries"][index], energyDemandQuerySetForBuilding[0].energy_amount.regular_time_series)

                energyDemandQuerySetForBuilding.update(**energyDemandInputValue)
            elif energyDemandQuerySetForBuilding.exists() and energyDemandQuerySetForBuilding[0].energy_amount is None:
                regularTimeSeriesUpdatedOrCreated = self._createOrUpdateRegularTimeSeries(dictForDatabase["RegularTimeSeries"][index])
                energyDemandQuerySetForBuilding.update(energy_amount=regularTimeSeriesUpdatedOrCreated, **energyDemandInputValue)      
            else:
                ngCityObjectQuerySet = NgCityObject.objects.filter(id__gmlid=buildingID)
                if ngCityObjectQuerySet.exists():
                    ngCityObject = ngCityObjectQuerySet[0]
                else:
                    ngCityObject = NgCityObject.objects.create(id=CityObject.objects.get(gmlid=buildingID))
                regularTimeSeriesUpdatedOrCreated = self._createOrUpdateRegularTimeSeries(dictForDatabase["RegularTimeSeries"][index])
                
                newEnergyDemand = EnergyDemand.objects.create(
                    cityObjectDemandsID=ngCityObject,
                    objectclass=ObjectClass.objects.get(id=50006),
                    **energyDemandInputValue,
                    energy_amount=regularTimeSeriesUpdatedOrCreated,
                )
            TimeSeries.objects.filter(id=regularTimeSeriesUpdatedOrCreated.id).update(**options["TimeSeries"])

    def _getObjectClass(self, className: str) -> ObjectClass:
        """Get the ObjectClass object from the database.

        """
        return ObjectClass.objects.get(classname=className)

    def _writeIntoDatabase(self, dictForDatabase, options) -> None:
        """Writes the values of the dictionary `dictForDatabase` into the database.

        `dictForDatabase` is a nested dictionary. In the first layer the keys are
        the names of the CityDB-Tables. The values are dictionaries whereby the keys
        are the names of the corresponding attributes.
        TODO: Refactor the whole function

        """
        self._writeEnergyDemandIntoDatabase(dictForDatabase, options)

    def _importFromFile(self, csv_file, buildingID, demandType):
        """Called, when option["input"] is a string and points to a file.

        """
        cityObjectOfBuildingList = CityObject.objects.filter(gmlid=options['buildingID'])
        cityObjectOfBuilding = cityObjectOfBuildingList[0]
        with open(options['input'], 'rt') as f:
            reader = csv.reader(f, dialect='excel')
            # if only one column is present create a virtual time step
            dataInFirstRow = next(reader)

            dataValuesStr = ""
            dataValuesStr += dataInFirstRow[0] + " "


            # Here starts the creation of the dummy time-data. 
            # it starts at the 01.01.2010 and as timedelta an hour is assumed.

            if len(dataInFirstRow) == 1:
                print("There is only a data-row and no time-information. It is assumed that the data is a aquired with a timedifference of one day.")
                counterForElements = 1
                for row in reader:
                    dataValuesStr += row[0] + " "
                    counterForElements += 1
                dataValuesStr = dataValuesStr[:-1]
                # create a virtual beginning and ending of the time series
                startDateTime = datetime(
                    year=2010,
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                )
                endDateTime = startDateTime + timedelta(hours=counterForElements)
                ## end of the creation of the dummy time-data

                regularTimeSeriesObjectClass = ObjectClass.objects.get(id=50033)
                
                newRegularTimeSeries = RegularTimeSeries.objects.create(
                    #  **cityObjectOfBuildingDict,
                    # _abst_time_series=newTimeSeriesObject,
                    # series_related_to=cityObjectOfBuilding,
                    objectclass=regularTimeSeriesObjectClass,
                    values=dataValuesStr,
                    values_uom="kWh",
                    timeperiodprop_beginposition=startDateTime, 
                    timeperiodproper_endposition=endDateTime,
                    timeinterval_unit="hour",
                    timeinterval=1,
                    timeinterval_factor=1,
                    timeinterval_radix=1,
                )

                correspondingTimeSeriesObj = TimeSeries.objects.filter(id=newRegularTimeSeries.id).last()
                correspondingTimeSeriesObj.acquisition_method = "simulation"
                correspondingTimeSeriesObj.interpolation_type = "averageInSucceedingInterval"
                correspondingTimeSeriesObj.quality_description = "add qualit description here"
                correspondingTimeSeriesObj.source = "EnergyPlus"
                correspondingTimeSeriesObj.thematic_description = "Heating energy"
                correspondingTimeSeriesObj.save()

                cityObjectOfBuilding = CityObject.objects.filter(gmlid=options['buildingID']).last()
                energyDemandObjectClass = ObjectClass.objects.get(id=50006)
                gmlIDForEnergyDemand = "GML_" + str(uuid.uuid4())

                if  len(NgCityObject.objects.filter(id=cityObjectOfBuilding.id)) == 0:
                    newNgCityObjectForEnergyDemand = NgCityObject.objects.create(
                        id=cityObjectOfBuilding,
                        )
                else:
                    newNgCityObjectForEnergyDemand = NgCityObject.objects.filter(id=cityObjectOfBuilding).last()
                newCityObjectForEnergyDemand = CityObject.objects.create(
                    gmlid=gmlIDForEnergyDemand,
                    objectclass=energyDemandObjectClass,
                    )
                if options["demandType"] == "electricalAppliances":
                    energyDemandObject = EnergyDemand.objects.create(
                        _parent_link=newCityObjectForEnergyDemand,
                        cityObjectDemandsID=newNgCityObjectForEnergyDemand,
                        end_use="electricalAppliances",
                        energy_amount=newRegularTimeSeries.timeseries_obj,
                        energy_carrier_type="electricity",
                        # maximum_load_uom="W",
                        )
                    # energyDemandObject.demands.add(cityObjectOfBuilding)
                    # energyDemandObject.save()
                elif options["demandType"] == "domesticHotWater":
                    energyDemandObject = EnergyDemand.objects.create(
                        _parent_link=newCityObjectForEnergyDemand,
                        cityObjectDemandsID=newNgCityObjectForEnergyDemand,
                        end_use="domesticHotWater",
                        energy_amount=newRegularTimeSeries.timeseries_obj,
                        energy_carrier_type="heat",
                        # maximum_load_uom="W",
                        )
                    # energyDemandObject.demands.add(cityObjectOfBuilding)
                    # energyDemandObject.save()
                

    def handle(self, *args, **options):
        """Load data into regular-time-series table from a csv file.

        """
        options["input"] = options["input"].replace("\'", "\"")
        inputAsPythonObj = json.loads(options["input"])
        optionalArguments = {
            "buildingID": options["buildingID"],
            "TimeSeries": {
                "acquisition_method": options["acquisition_method"],
                "interpolation_type": options["interpolation_type"],
                "quality_description": options["quality_description"],
                "source": options["source"],
                "thematic_description": options["thematic_description"],
            }
        }
        # check of which python type is the options["input"]. 
        if isinstance(inputAsPythonObj, dict):
            dictForDatabase = self._parseDict(inputAsPythonObj)
            self._writeIntoDatabase(dictForDatabase, optionalArguments)
        elif isinstance(inputAsPythonObj, str):
            self._importFromFile(inputAsPythonObj, options["buildingID"], options["demandType"])
        else:
            raise ValueError("The input is neither a dictionary nor a string.")


