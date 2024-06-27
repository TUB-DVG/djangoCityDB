from datetime import datetime
import json
import random
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from citydb.models import (
    Building,
    CityObject,
    EnergyDemand,
    RegularTimeSeries,
)

class TestTimeSeriesImport(TestCase):
    """Test if the timeseries data is present after import.

    """
    def setUp(self):
        """Called before every test-method

        """
        querySetOfBuildingGMLIDs = Building.objects.all().values_list("gmlid", flat=True)
        self.randomBuildingGMLID = random.choice(querySetOfBuildingGMLIDs)
        self.chosenEnergyDemandType = random.choice(["electricalAppliances", "domesticHotWater"])

    def testTimeseriesForFZKHousePresent(self):
        """Test if the TimeSeries for the FZK House is present.

        """
        cityObjectOfBuilding = CityObject.objects.get(gmlid="GML_257a8dde-8194-4ca3-b581-abd591dcd6a3")
        timeSeries = RegularTimeSeries.objects.get(series_related_to=cityObjectOfBuilding)

    def testImportTimeSeriesWithDIfferentTypes(self):
        """

        """
        # stringify the python-object:
        pythonObjForCommand = []
        stringifiedInput = json.dumps(pythonObjForCommand)

        self.assertRaises(
            ValueError,
            call_command,
            "import_timeseries", 
            stringifiedInput,
            self.randomBuildingGMLID,
            self.chosenEnergyDemandType,
        )

    def testToSpecifyAddionalOptions(self):
        """

        """
        # stringify the python-object:
        pythonObjForCommand = {
            "DATE": ["2010-01-01 0:00:00", "2010-01-02 1:00:00", "2010-01-03 2:00:00"],
            f"{self.chosenEnergyDemandType}_kWh": [1.0, 2.0, 3.0],
        }
        additionalOptions = {
            "acquisition_method": "simulation",
            "interpolation_type": "averageInSucceedingInterval",
            "quality_description": "add qualit description here",
            "source": "EnergyPlus",
            "thematic_description": "Heating energy",
        }
        stringifiedInput = json.dumps(pythonObjForCommand)
        breakpoint()
        call_command("import_timeseries", stringifiedInput, self.randomBuildingGMLID, **additionalOptions)
        # self.assertRaises(
        #     ValueError,

        # )

    def testUpdateDomesticHotWater(self):
        """Re-import Domestic hot water energy demand and test if it the RegularTimeSeries is updated.

        If a RegularTimeSeries and a EnergyDemand already exist for the specified building and demand type, 
        the RegularTimeSeries should be updated and no new RegularTimeSeries should be created.

        """
        buildingId = "BLDG_0003000b0054e8af"
        energyDemandType = "domesticHotWater"
        dictOfTimeSeries = {
            "DATE": ["2010-01-01 0:00:00", "2010-01-02 1:00:00", "2010-01-03 2:00:00"],
            f"{energyDemandType}_kWh": [1.0, 2.0, 3.0],
        }
        stringifiedInput = json.dumps(dictOfTimeSeries)
        
        # get the object state before the import:
        energyDemandBeforeImport = EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType)
        idOfReagularTimeSeries = energyDemandBeforeImport.energy_amount.regular_time_series.id
        
        call_command("import_timeseries", stringifiedInput, buildingId)

        # get the object state after the import:
        energyDemandAfterImport = EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType)
        idOfReagularTimeSeriesAfterImport = energyDemandAfterImport.energy_amount.regular_time_series.id

        self.assertEqual(idOfReagularTimeSeries, idOfReagularTimeSeriesAfterImport, "The ID of the RegularTimeSeries connected to the EnergyDemand should not change after the import. It should be updated instead.")
        self.assertEqual(energyDemandAfterImport.energy_amount.regular_time_series.values, "1.0 2.0 3.0", "The values of the RegularTimeSeries should be updated after the import.")
        self.assertEqual(energyDemandAfterImport.end_use, energyDemandType, "The end_use of the EnergyDemand should not change after the import.")

    def testImportMultipleEnergyDemands(self):
        """Test if multiple EnergyDemands can be imported at once.

        """
        buildingId = "BLDG_0003000b0054e8af"
        energyDemandType1 = "domesticHotWater"
        energyDemandType2 = "electricalAppliances"
        dictOfTimeSeries = {
            "DATE": ["2010-01-01 0:00:00", "2010-01-02 1:00:00", "2010-01-03 2:00:00"],
            f"{energyDemandType1}_kWh": [1.0, 2.0, 3.0],
            f"{energyDemandType2}_Scale": [4.0, 5.0, 6.0],
        }
        stringifiedInput = json.dumps(dictOfTimeSeries)
        
        call_command("import_timeseries", stringifiedInput, buildingId)

        # check if there are two EnergyDemands for the specified building:
        self.assertTrue(EnergyDemand.objects.filter(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType1).exists(), "The EnergyDemand for the first demand type should be present after the import.")
        self.assertTrue(EnergyDemand.objects.filter(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType2).exists(), "The EnergyDemand for the second demand type should be present after the import.")

        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType1).energy_amount.regular_time_series.values, "1.0 2.0 3.0", "The values of the RegularTimeSeries for the first demand type should be correct.")
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType2).energy_amount.regular_time_series.values, "4.0 5.0 6.0", "The values of the RegularTimeSeries for the second demand type should be correct.")

        # check if the unit is correct:
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType1).energy_amount.regular_time_series.values_uom, "kWh", "The unit of the RegularTimeSeries for the first demand type should be 'kWh'.")
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType2).energy_amount.regular_time_series.values_uom, "Scale", "The unit of the RegularTimeSeries for the second demand type should be 'Scale'.")

        # check if the time unit is written correctly:
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType1).energy_amount.regular_time_series.timeinterval_unit, "hour", "The time interval of the RegularTimeSeries for the first demand type should be 'hour'.")
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType2).energy_amount.regular_time_series.timeinterval_unit, "hour", "The time interval of the RegularTimeSeries for the second demand type should be 'hour'.")

        # check if the timedifference is written correctly, it should be 25 hours:
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType1).energy_amount.regular_time_series.timeinterval, 25, "The timeinterval should 25 hours.")
        self.assertEqual(EnergyDemand.objects.get(cityObjectDemandsID__id__gmlid=buildingId, end_use=energyDemandType2).energy_amount.regular_time_series.timeinterval, 25, "The timeinterval should 25 hours.")

    def testImportOfTimeSeriesViaDict(self):
        """Test if import via Dictionary is working and produces right timedelta representation in the database.
        
        This test imports a timeseries, which is composed of just 3 values. It is tested if the timedelta is 
        """
        dictOfTimeSeries = {
            "DATE": ["2010-01-01 0:00:00", "2010-01-02 1:00:00", "2010-01-03 2:00:00"],
            f"{self.chosenEnergyDemandType}_kWh": [1.0, 2.0, 3.0],
        }

        # check which building are present in the database and return a list of the gmlids
        querySetOfBuildingGMLIDs = Building.objects.all().values_list("gmlid", flat=True)
        randomBuildingGMLID = random.choice(querySetOfBuildingGMLIDs)
        stringifiedInput = json.dumps(dictOfTimeSeries)
        call_command("import_timeseries", stringifiedInput, randomBuildingGMLID)

        # check if there is an energyDemand of the specified type for the chosen building:
        self.assertTrue(
            EnergyDemand.objects.filter(
                cityObjectDemandsID__id__gmlid=self.randomBuildingGMLID,
                end_use=self.chosenEnergyDemandType,
            ).exists(),
            "In the EnergyDemand-Table no object for the specifed building and demand type is present. Even after 'import_timeseries' was called.",
        )
        # check if a RegularTimeSeries is present for the specified building and demand type:
        regularTimeSeriesForBuilding = RegularTimeSeries.objects.filter(
            series_related_to__gmlid=self.randomBuildingGMLID,
            demand_type=self.chosenEnergyDemandType,
        )
        if not regularTimeSeriesForBuilding.exists():
            self.fail("No RegularTimeSeries for the specified building and demand type is present. After 'import_timeseries' was called.")
        else:
            if len(regularTimeSeriesForBuilding) > 1:
                self.fail("There are more than one RegularTimeSeries for the specified building and demand type. If 'import_timeseries' was called and a RegularTimeSeries was present before, it should be updated and not created again.")
            else:
                regularTimeSeries = regularTimeSeriesForBuilding[0]
                # check if the time data is correct:
                self.assertEqual(regularTimeSeries.values, dictOfTimeSeries[f"{self.chosenEnergyDemandType}_kWh"].split(" "), "The data-values inside the RegularTimeSeries row should be an space separated list")
                self.assertEqual(regularTimeSeries.values_uom, "kWh", "The unit of measurement for the values in the RegularTimeSeries is not 'kWh'. This is unexpected.")
                self.assertEqual(regularTimeSeries.timeinterval_unit, "hour", "The time interval of the RegularTimeSeries is not 'hour'. This is unexpected.")
                self.assertEqual(regularTimeSeries.timeinterval_factor, "1", "Timeintervall factor should be 1")
                self.assertEqual(regularTimeSeries.timeinterval_radix, "1", "Timeintervall radix should be 1")
                
                beginingDateTime = datetime.strptime(dictOfTimeSeries["DATE"][0], "%Y-%m-%d %H:%M:%S")
                endDateTime = datetime.strptime(dictOfTimeSeries["DATE"][-1], "%Y-%m-%d %H:%M:%S")
                self.assertEqual(regularTimeSeries.timeperiodprop_beginposition, beginingDateTime, "beginning of the time series is not correct")
                self.assertEqual(regularTimeSeries.timeperiodproper_endposition, endDateTime, "beginning of the time series is not correct")

class TestReadTimeSeries(TestCase):
    """Test if reading demand-timeseries data is working correctly.

    """
    def testReadSingleDemand(self):
        """test if a single demand can read using the optional flag.

        """
        out = StringIO()
        call_command("read_timeseries", "EnergyDemand", "BLDG_0003000b0054e8af", "--end_use", "domesticHotWater", stdout=out)

        returnDictSerialized = out.getvalue()
        returnDict = json.loads(returnDictSerialized)
        breakpoint()
        self.assertTrue("domesticHotWater_kWh" in returnDict, "The key for the domestic hot water demand is not present in the returned dictionary.")
        self.assertEqual(len(list(returnDict.keys())), 1, "Only one demand should be present in the returned dictionary.")