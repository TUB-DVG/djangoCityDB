import csv
from datetime import (
    datetime,
    timedelta,
)
import uuid

from django.core.management import BaseCommand
import pandas as pd
from io import StringIO

from citydb.models import (
    CityObject,
    Building,
    EnergyBuilding,
    DailySchedule,
    Occupants,
    ObjectClass,
    RegularTimeSeries, 
    TimeSeries,
    TimeSeriesSchedule,
    UsageZone,
    NgPeriodOfYear,
)

class Command(BaseCommand):
    help = 'Load a csv file into the database'

    LIST_OF_SCHEDDULES = [
        "coolingSchedule",
        "heatingSchedule",
        "ventilationSchedule",
        "occupancyRate",
    ]

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("buildingID", type=str, help="The ID of the building to which the time series belongs to.")

    def _createUsageZoneAttrtStrFromDictKey(self, key: str) -> str:
        """Create a string for the usage zone attribute from the key.

        Parameters
        ----------
        key: str
            A key from the input dictionary.

        Returns
        -------
        str
            A string which can be used as an attribute for the UsageZone object.
        """
        scheduleWithoutUnit = key.split("_")[0]
        typeOfSchedule =scheduleWithoutUnit.split("Schedule")[0]
        return typeOfSchedule + "_schedule"

    def _getOrCreateUsageZoneObject(self, buildingID: str) -> UsageZone:
        """

        """

        usageZoneObjForBuilding = UsageZone.objects.filter(building___parent_link_eb__gmlid=buildingID)
        if usageZoneObjForBuilding.exists():
            usageZoneObjForBuilding = usageZoneObjForBuilding[0]
        else:
            usageZoneObjForBuilding = UsageZone.objects.create(
                building=CityObject.objects.get(gmlid=buildingID),
                objectclass=self._getObjectClass("UsageZone"),
            )
        return usageZoneObjForBuilding

    def _createPeriodOfYear(self, dictForDatabase, options, usageZoneObjForBuilding) -> NgPeriodOfYear:
        """Create a PeriodOfYear object.

        Check if a periodOfYear object already exists. For the schedule and buildingID. 
        If not create a new one.

        Problems:
        ---------
        - For some reasons the automatic incrementation of the id does not work.
        """
        dictPeriodOfYearForSchedule = {}
        for key in list(dictForDatabase.keys()):
            if key == "occupancyRate":
                usageZoneObjForBuilding[0].occupants.all()
                ngScheduleIds = UsageZone.objects.all()[0].occupants.all().values_list("occupancy_rate_id", flat=True)
                existingPeriodOfYearRows = NgPeriodOfYear.objects.filter(schedule_periodofyear_id__in=ngScheduleIds)
            else:

                dictPeriodOfYearForSchedule[key] = None
                attributeNameForKey = self._constructForeignKeyUsageZone(key)
                listOfNgScheduleIds = usageZoneObjForBuilding.values_list(
                    attributeNameForKey,
                    flat=True,
                )
                existingPeriodOfYearRows = NgPeriodOfYear.objects.filter(schedule_periodofyear_id__in=listOfNgScheduleIds)

            if not existingPeriodOfYearRows.exists():
                if len(NgPeriodOfYear.objects.all()) > 0:
                    periodOfYearBiggestId = NgPeriodOfYear.objects.all().order_by('-id').first().id + 1
                else:
                    periodOfYearBiggestId = 0

                scheduleObj = TimeSeriesSchedule.objects.create(
                    objectclass=self._getObjectClass("DailyPatternSchedule"),
                    gmlid="GML_" + str(uuid.uuid4()),
                )

                newPeriodOfYearObj = NgPeriodOfYear.objects.create(
                    id=periodOfYearBiggestId,
                    objectclass=self._getObjectClass("PeriodOfYear"),
                    schedule_periodofyear_id=scheduleObj,
                    timeperiodprop_beginposition=self.TIMEPERIODPROP_BEGINPOSITION,
                    timeperiodproper_endposition=self.TIMEPERIODPROPER_ENDPOSITION,
                )
                dictPeriodOfYearForSchedule[key] = newPeriodOfYearObj
            else:
                dictPeriodOfYearForSchedule[key] = existingPeriodOfYearRows[0]

        return newPeriodOfYearObj

    def _createDailyScheduleAndTimeSeries(self, dictForDatabase, options) -> None:
        """Iterate through the schedule-input dict and create the DailySchedules and TimeSeries.

        Parameters
        ----------
        dictForDatabase: dict
            A dictionary with the schedule data.
        options: dict

        Returns
        -------
        DdailySchedule: The created DailySchedule object.

        """
        regularTimeSeriesObj = self._createOrUpdateRegularTimeSeries(dictForDatabase["RegularTimeSeries"])
        dailyScheduleObj = DailySchedule.objects.create(
            periodofyear_dailyschedul_id=idOfPeriodOfYear,
            daytype=typeOfDay,
            regulartimeseries=regularTimeSeriesObj,
        )
        TimeSeries.objects.filter(id=regularTimeSeriesObj.id).update(**options["TimeSeries"])
        
        return dailyScheduleObj


    def _constructForeignKeyUsageZone(self, keyInScheduleDict: str) -> UsageZone:
        """

        """
        if keyInScheduleDict == "heatingSchedule":
            return "heating_schedule_id"
        elif keyInScheduleDict == "coolingSchedule":
            return "cooling_schedule_id"
        elif keyInScheduleDict == "ventilationSchedule":
            return "ventilation_schedule_id"
        elif keyInScheduleDict == "occupancyRate":
            return "occupancyrate_id"
        else:
            raise ValueError("The key in the schedule-dict is not recognized.")

    def _identifyEnergyDemandAndScheduleColumns(self, listOfDictKeys: list) -> dict:
        """Split columns in schedule- and energyDemand-columns.

        This function identifies all keys which are of type energyDemand and schedule.
        All keys of type energyDemand are put inside a list under `returnDict["EnergyDemand"]`
        and all keys of type schedule are put inside a list under `returnDict["Schedule"]`.

        Parameters
        ----------
        listOfDictKeys: list
            A list of keys of the input dictionary.

        Returns
        -------
        dict
            A dictionary with the keys "EnergyDemand" and "Schedule". The values are lists.
    

        """
        returnDict = {
            "EnergyDemand": [],
            "Schedule": [],
        }
        for key in listOfDictKeys:
            if key.split("_")[0] in self.LIST_OF_ENERGYDEMAND_ENDUSES:
                returnDict["EnergyDemand"].append(key)
            elif key.split("_")[0] in self.LIST_OF_SCHEDDULES:
                returnDict["Schedule"].append(key)
            else:
                print(f"Can not categorize the key: {key} as schedule or EnergyDemand. The key is ignored.")
        return returnDict

    def _writeScheduleIntoDatabase(self, dictForDatabase, options) -> None:
        """Write the Schedules from the input into the database.

        """
        buildingID = options.pop("buildingID", None)
        # find out if the current schedule `scheduleElement` is already in the database.
        # And needs to be updated.
        usageZoneObjForBuilding = self._getOrCreateUsageZoneObject(buildingID)

        # create a new periodOfYear objects
        dictOfPeriodOfYear = self._createPeriodOfYear(dictForDatabase, options, usageZoneObjForBuilding)

        # usageZoneObjForBuilding = UsageZone.objects.filter(building___parent_link_eb__gmlid=buildingID)
        if usageZoneObjForBuilding.exists():
            usageZoneObjForBuilding = usageZoneObjForBuilding[0]
            for scheduleElement in list(dictForDatabase.keys()):
                dictOfSchedule = dictForDatabase[scheduleElement]
                scheduleAttrStr = self._createUsageZoneAttrtStrFromDictKey(scheduleElement)
                idOfPeriodOfYear = usageZoneObjForBuilding.__getattribute__(scheduleAttrStr).ngperiodofyear_set.values()[0]["id"]
                dailyScheduleObjs = DailySchedule.objects.filter(periodofyear_dailyschedul_id=idOfPeriodOfYear)
                # remove the regulartimeseries and timeseries and create new ones:
                for typeOfDay in ["weekDay", "weekEnd"]:
                    dailyScheduleForDayType = dailyScheduleObjs.filter(daytype=typeOfDay)
                    if dailyScheduleForDayType.exists():
                        dictOfScheduleOfDayType = dictOfSchedule[typeOfDay]      
                        for key in list(dictOfScheduleOfDayType["RegularTimeSeries"].keys()):
                            settatr(dailyScheduleForDayType.schedule_id.regular_time_series, key, dictOfScheduleOfDayType["RegularTimeSeries"][key])
                        dailyScheduleForDayType.schedule_id.regular_time_series.save()
                        for key in list(options["TimeSeries"].keys()):
                            setattr(dailyScheduleForDayType.schedule_id.regular_time_series.timeseries_obj, key, options["TimeSeries"][key])
                        dailyScheduleForDayType.schedule_id.timeseries_obj.save()
                    else:
                        dailyScheduleForDayType = self._createDailyScheduleAndTimeSeries(dictOfScheduleOfDayType, options)

                        # create a new periodOfYear object


                for dailySchedule in dailyScheduleObjs:
                    breakpoint()
                    dailySchedule.regulartimeseries_set.all().delete()
                    dailySchedule.timeseries_set.all().delete()
            self._createDailySchedulesAndTimeSeries(dictForDatabase, options)
        else:
            # create usageZone-object for building:
            for scheduleElement in list(dictForDatabase.keys()):
                self._createDailySchedulesAndTimeSeries(dictForDatabase, options)


    def _timeProcessing(self, dictOfTimeSeries: dict, dictOfCategorizedKeys: list) -> tuple:
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
            returns list of datetime-objects and a dictionary with the categorized data. 
            Wrapped inside a tuple. 
        """
        datetimeObjList = []
        lastTimeDifference = None
        dictScheduleSplitWeekday = {}
        for key in dictOfCategorizedKeys["Schedule"]:
            dictScheduleSplitWeekday[key] = {
                "weekDay": {
                    "time": [],
                    "values": [],
                },
                "weekEnd": {
                    "time": [],
                    "values": [],
                },
            }
        
        for index, datetimeStr in enumerate(dictOfTimeSeries['DATE']):
            datetimeObj = datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M:%S')
            if datetimeObj.weekday() < 5:
                # weekday
                for key in dictOfCategorizedKeys["Schedule"]:
                    dictScheduleSplitWeekday[key]["weekday"]["time"].append(datetimeObj)
                    dictScheduleSplitWeekday[key]["weekday"]["values"].append(datetimeObj)
            else:
                # weekend
                for key in dictOfCategorizedKeys["Schedule"]:
                    dictScheduleSplitWeekday[key]["weekend"]["time"].append(datetimeObj)
                    dictScheduleSplitWeekday[key]["weekend"]["values"].append(datetimeObj)
            datetimeObjList.append(datetimeObj)

    def handle(self, *args, **options):
        """Load data into regular-time-series table from a csv file.

        """

        cityObjectOfBuildingList = CityObject.objects.filter(gmlid=options['buildingID'])
        cityObjectOfBuilding = cityObjectOfBuildingList[0]

        with open(options['csv_file'], 'rt') as f:
            reader = csv.reader(f, dialect='excel')
            # if only one column is present create a virtual time step
            dataInFirstRow = next(reader)

            dataValuesStr = ""
            heatingScheduleDataStr = ""
            ventilationScheduleDataStr = ""
            dataValuesStr += dataInFirstRow[0] + " "
            if len(dataInFirstRow) == 1:
                print("There is only a data-row and no time-information. It is assumed that the data is a aquired with a timedifference of one day.")
                counterForElements = 1
                for row in reader:
                    dataValuesStr += row[0] + " "
                    heatingScheduleDataStr += "18" + " "
                    ventilationScheduleDataStr += "30" + " "
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
                # endDateTime = startDateTime.replace(hour=startDateTime.hour + counterForElements)
                # breakpoint()
                # cityObjectOfBuildingDict = cityObjectOfBuilding.__dict__
                # cityObjectOfBuildingDict.pop('_state', None)
                # cityObjectOfBuildingDict.pop('id', None)
                # newTimeSeriesObject = TimeSeries.objects.create(
                #     **cityObjectOfBuildingDict,
                #     # quality_description=options['csv_file'],
                #     # _parent_link=cityObjectOfBuilding,
                #     # objectclass=cityObjectOfBuilding.objectclass,
                #     )


                #create a RegularTimeSeries object for the occupancyRate, the headingSchedule and the ventilationSchedule
                # for that we need 3 objectClass-objects of type RegularTimeSeries:
                regularTimeSeriesOccupancyRate = ObjectClass.objects.get(id=50033)
                regularTimeSeriesHeatingSchedule = ObjectClass.objects.get(id=50033)
                regularTimeSeriesVentilationSchedule = ObjectClass.objects.get(id=50033)

                regularTimeSeriesOccupancyRate = RegularTimeSeries.objects.create(
                    # _abst_time_series=newTimeSeriesObject,
                    # series_related_to=cityObjectOfBuilding,
                    objectclass=regularTimeSeriesOccupancyRate,
                    gmlid="GML_" + str(uuid.uuid4()),
                    values=dataValuesStr,
                    values_uom="1",
                    timeperiodprop_beginposition=startDateTime, 
                    timeperiodproper_endposition=endDateTime,
                    timeinterval_unit="hour",
                    timeinterval=1,
                    timeinterval_factor=1,
                    timeinterval_radix=1,
                )

                # breakpoint()
                # set default values for the aquiisition_method, interpolation_type, quality_description, source and thematic_description
                # of the TimeSeries-object to avoid validation errors:
                regularTimeSeriesOccupancyRate.timeseries_obj.acquisition_method = "simulation"
                regularTimeSeriesOccupancyRate.timeseries_obj.interpolation_type = "averageInSucceedingInterval"
                regularTimeSeriesOccupancyRate.timeseries_obj.quality_description = "add qualit description here"
                regularTimeSeriesOccupancyRate.timeseries_obj.source = "EnergyPlus"
                regularTimeSeriesOccupancyRate.timeseries_obj.thematic_description = "Occupancy rate"

                regularTimeSeriesHeatingSchedule = RegularTimeSeries.objects.create(
                    # _abst_time_series=newTimeSeriesObject,
                    # series_related_to=cityObjectOfBuilding,
                    objectclass=regularTimeSeriesHeatingSchedule,
                    gmlid="GML_" + str(uuid.uuid4()),
                    values=heatingScheduleDataStr,
                    values_uom="C",
                    timeperiodprop_beginposition=startDateTime, 
                    timeperiodproper_endposition=endDateTime,
                    timeinterval_unit="hour",
                    timeinterval=1,
                    timeinterval_factor=1,
                    timeinterval_radix=1,
                )

                regularTimeSeriesHeatingSchedule.timeseries_obj.acquisition_method = "simulation"
                regularTimeSeriesHeatingSchedule.timeseries_obj.interpolation_type = "averageInSucceedingInterval"
                regularTimeSeriesHeatingSchedule.timeseries_obj.quality_description = "add qualit description here"
                regularTimeSeriesHeatingSchedule.timeseries_obj.source = "EnergyPlus"
                regularTimeSeriesHeatingSchedule.timeseries_obj.thematic_description = "Heating energy"

                regularTimeSeriesVentilationSchedule= RegularTimeSeries.objects.create(
                    # _abst_time_series=newTimeSeriesObject,
                    # series_related_to=cityObjectOfBuilding,
                    objectclass=regularTimeSeriesVentilationSchedule,
                    gmlid="GML_" + str(uuid.uuid4()),
                    values=ventilationScheduleDataStr,
                    values_uom="C",
                    timeperiodprop_beginposition=startDateTime, 
                    timeperiodproper_endposition=endDateTime,
                    timeinterval_unit="hour",
                    timeinterval=1,
                    timeinterval_factor=1,
                    timeinterval_radix=1,
                )

                regularTimeSeriesVentilationSchedule.timeseries_obj.acquisition_method = "simulation"
                regularTimeSeriesVentilationSchedule.timeseries_obj.interpolation_type = "averageInSucceedingInterval"
                regularTimeSeriesVentilationSchedule.timeseries_obj.quality_description = "add qualit description here"
                regularTimeSeriesVentilationSchedule.timeseries_obj.source = "EnergyPlus"
                regularTimeSeriesVentilationSchedule.timeseries_obj.thematic_description = "Ventilation rate"

                # end of creation of RegularTimeSeries-objects

                # create 3 objectClass-objects of type DailyPatternSchedule
                # and write the corresponding IDs into the ng_schedule-table
                dailyPatternScheduleOccupancyRate = ObjectClass.objects.get(id=50030)
                dailyPatternScheduleHeatingSchedule = ObjectClass.objects.get(id=50030)
                dailyPatternScheduleVentilationSchedule = ObjectClass.objects.get(id=50030)

                # create the corresponding rows in the ng_schedule-table
                scheduleObjOccupancyRate = TimeSeriesSchedule.objects.create(
                    objectclass=dailyPatternScheduleOccupancyRate,
                    gmlid="GML_" + str(uuid.uuid4()),
                )
                scheduleObjHeatingSchedule = TimeSeriesSchedule.objects.create(
                    objectclass=dailyPatternScheduleHeatingSchedule,
                    gmlid="GML_" + str(uuid.uuid4()),
                )
                scheduleObjVentilationSchedule = TimeSeriesSchedule.objects.create(
                    objectclass=dailyPatternScheduleVentilationSchedule,
                    gmlid="GML_" + str(uuid.uuid4()),
                )
                # end of creation of TimeSeriesSchedule-objects

                # on some reasons the primaryField is not set automatically
                # so we have to set it manually
                # breakpoint()
                if len(NgPeriodOfYear.objects.all()) > 0:
                    periodOfYearBiggestId = NgPeriodOfYear.objects.all().order_by('-id').first().id + 1
                else:
                    periodOfYearBiggestId = 0

                # create 3 periodOfYear-objects and connect them to the dailyPatternSchedule-objects
                periodOfYearObjOccupancyRate = NgPeriodOfYear.objects.create(
                    id=periodOfYearBiggestId,
                    schedule_periodofyear_id=scheduleObjOccupancyRate,
                    timeperiodprop_beginposition=startDateTime,
                    timeperiodproper_endposition=endDateTime,
                )     
                periodOfYearObjHeatingRate = NgPeriodOfYear.objects.create(
                    id=periodOfYearBiggestId+1,
                    schedule_periodofyear_id=scheduleObjHeatingSchedule,
                    timeperiodprop_beginposition=startDateTime,
                    timeperiodproper_endposition=endDateTime,
                )     
                periodOfYearObjVentilationSchedule = NgPeriodOfYear.objects.create(
                    id=periodOfYearBiggestId+2,
                    schedule_periodofyear_id=scheduleObjVentilationSchedule,
                    timeperiodprop_beginposition=startDateTime,
                    timeperiodproper_endposition=endDateTime,
                )
                # end of creation of PeriodOfYear-objects

                if len(DailySchedule.objects.all()) > 0:

                    dailyScheduleBiggestId = DailySchedule.objects.all().order_by('-id').first().id + 1
                else:
                    dailyScheduleBiggestId = 0

                # create 3 DailySchedule-objects
                # these objects connect periodOfYear with the timeseries-object
                dailyScheduleObjOccupancyRate = DailySchedule.objects.create(
                    id=dailyScheduleBiggestId,
                    schedule_id=regularTimeSeriesOccupancyRate.timeseries_obj,
                    daytype="weekDay",
                    periodofyear_dailyschedul_id=periodOfYearObjOccupancyRate,
                )
                dailyScheduleObjHeatingSchedule = DailySchedule.objects.create( 
                    id=dailyScheduleBiggestId+1,
                    schedule_id=regularTimeSeriesHeatingSchedule.timeseries_obj,
                    daytype="weekDay",
                    periodofyear_dailyschedul_id=periodOfYearObjHeatingRate,
                )
                dailyScheduleObjVentilationSchedule = DailySchedule.objects.create(
                    id=dailyScheduleBiggestId+2,
                    schedule_id=regularTimeSeriesVentilationSchedule.timeseries_obj,
                    daytype="weekDay",
                    periodofyear_dailyschedul_id=periodOfYearObjVentilationSchedule,
                )

                # create an object of type UsageZone
                df = pd.read_csv(StringIO(dataValuesStr), header=None, delimiter=" ")
                # Compute the average
                average = df.mean().values[0]

                numberOfOccupants = df.max().values[0]

                # get building-id of building:
                buildingObjectForBuildingGMLID = Building.objects.get(id=cityObjectOfBuilding.id)

                # check if an EnergyBuild-object exists for the id of the building, which corresponds to the gmlid
                # given in the command-line arguments:
                try:                    
                    ngBuildingForCityObj = EnergyBuilding.objects.get(_parent_link_eb_id=buildingObjectForBuildingGMLID.id)
                except:
                    # breakpoint()
                    # ngBuidlingObj = EnergyBuilding.objects.create(building_obj=Building.objects.get(id=cityObjectOfBuilding.id),)
                    ngBuildingForCityObj = EnergyBuilding.objects.create(
                        # _parent_link_eb=Building.objects.get(id=cityObjectOfBuilding.id),
                        _parent_link_eb=buildingObjectForBuildingGMLID,
                        # objectclass=ObjectClass.objects.get(id=26),
                        # gmldid=cityObjectOfBuilding.gmlid,
                    )
                usageZoneClassObj = ObjectClass.objects.get(id=50028)
                usageZoneObj = UsageZone.objects.create(
                    objectclass=usageZoneClassObj,
                    gmlid="GML_" + str(uuid.uuid4()),
                    building=ngBuildingForCityObj,
                    heating_schedule=scheduleObjHeatingSchedule,
                    ventilation_schedule=scheduleObjVentilationSchedule,
                    usage_zone_type="home",
                )

                # create an object of type Occupants
                occupantsObjectClassObj = ObjectClass.objects.get(id=50027)
                occupantsObj = Occupants.objects.create(
                    objectclass=occupantsObjectClassObj,
                    gmlid="GML_" + str(uuid.uuid4()),
                    number_of_occupants=numberOfOccupants,
                    occupancy_rate=scheduleObjOccupancyRate,
                    usage_zone_occupied_by=usageZoneObj,
                )


                # correspondingTimeSeriesObj = TimeSeries.objects.filter(id=newRegularTimeSeries.id).last()
                # correspondingTimeSeriesObj.acquisition_method = "simulation"
                # correspondingTimeSeriesObj.interpolation_type = "averageInSucceedingInterval"
                # correspondingTimeSeriesObj.quality_description = "add qualit description here"
                # correspondingTimeSeriesObj.source = "EnergyPlus"
                # correspondingTimeSeriesObj.thematic_description = "Heating energy"
                # correspondingTimeSeriesObj.save()
                # breakpoint()
                # cityObjectOfBuilding = CityObject.objects.filter(gmlid=options['buildingID']).last()
                # newRegularTimeSeries.series_related_to.add(cityObjectOfBuilding)
                # newRegularTimeSeries.save()
                # dailyScheduleObjClassObj = ObjectClass.objects.get(id=50030)
                # periodOfYearObjClassObj = ObjectClass.objects.get(id=50031)

            

                # # scheduleObj = TimeSeriesSchedule.objects.create(
                # #     objectclass=dailyScheduleObjClassObj,
                # # )                
                # newDailyScheduleObj = DailySchedule.objects.create(
                #     objectclass=dailyScheduleObjClassObj,
                #     # id=3,
                #     schedule_id=correspondingTimeSeriesObj,
                # )



                
                # occupantsObj = Occupants.objects.create(
                #     objectclass=ObjectClass.objects.get(id=50027),
                #     number_of_occupants=numberOfOccupants,
                #     occupancy_rate=scheduleObj,
                # )
                # 50024
                # abstractSchedule = ObjectClass.objects.get(id=50024)
                # scheduleIncludingRateOfOccupancy = TimeSeriesSchedule.objects.create(
                #     # **cityObjectOfBuildingDict,
                #     # _parent_link=cityObjectOfBuilding,
                #     objectclass=abstractSchedule,
                #     average_value=average,
                #     average_value_uom="1",
                #     # objectclass_schedule=cityObjectOfBuilding.objectclass,
                #     time_depending_values=correspondingTimeSeriesObj,
                #     )




                # create a new occupant-object and link it to the imported regular-time-series
                # newOccupant = Occupants.objects.create(
                #     # **cityObjectOfBuildingDict,
                #     objectclass=ObjectClass.objects.get(id=50027),
                #     # _parent_link=cityObjectOfBuilding,
                #     occupancy_rate=scheduleIncludingRateOfOccupancy,
                #     number_of_occupants=numberOfOccupants,
                #     )
                