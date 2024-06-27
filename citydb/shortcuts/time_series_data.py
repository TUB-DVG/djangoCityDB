"""Documentation missing."""
from datetime import datetime as dt
import time
from citydb.models import ObjectClass
from citydb.models import IrregularTimeSeriesFile
from citydb.models import AbstractEnergySystem
from citydb.shortcuts import buildings_data as bd_short
import numpy as np
import os
import calibration.utils.owncloud as owncloud


def get_time_series_object(building, end_use, thematic_description, acquisition_method):
    """Documentation missing."""
    object_dict = {
        "spaceHeating": "GenericConversionSystem",
        "ventilationHeating": "MechanicalVentilation",
        "otherOrCombinationHeating": "HeatExchanger",
        "otherOrCombinationCooling": "HeatExchanger",
    }
    try:
        time_series_object = (
            building.energy_system.get(
                objectclass=ObjectClass.objects.get(classname=object_dict[end_use]),
                energy_conversion_system_obj__system_operation__end_use=end_use,
            )
            .energy_conversion_system_obj.system_operation.get(end_use=end_use)
            .series_related_to.get(
                thematic_description=thematic_description,
                acquisition_method=acquisition_method,
            )
        )
        return time_series_object
    except (IrregularTimeSeriesFile.DoesNotExist, AbstractEnergySystem.DoesNotExist):
        return None


def get_time_series_data(
    building,
    end_use,
    thematic_description,
    acquisition_method,
    start=dt(2014, 1, 1, 0, 0, 0),
    end=dt.now(),
    mean="1h",
    csv=False,
    workspace=None,
    remote_path=None,
):
    """Documentation missing."""
    object_dict = {
        "spaceHeating": "GenericConversionSystem",
        "ventilationHeating": "MechanicalVentilation",
    }
    if csv is False:
        try:
            time_series_object = (
                building.energy_system.get(
                    objectclass=ObjectClass.objects.get(classname=object_dict[end_use]),
                    energy_conversion_system_obj__system_operation__end_use=end_use,
                )
                .energy_conversion_system_obj.system_operation.get(end_use=end_use)
                .series_related_to.get(
                    thematic_description=thematic_description,
                    acquisition_method=acquisition_method,
                )
            )
            return {
                "time_series_object": time_series_object,
                "time_series_values": time_series_object.get_values(
                    start=start, end=end, mean=mean
                ),
            }
        except (
            IrregularTimeSeriesFile.DoesNotExist,
            AbstractEnergySystem.DoesNotExist,
        ):
            return {"time_series_object": None, "time_series_values": 0.0}
    if csv is True:

        try:
            time_series_object = (
                building.energy_system.get(
                    objectclass=ObjectClass.objects.get(classname=object_dict[end_use]),
                    energy_conversion_system_obj__system_operation__end_use=end_use,
                )
                .energy_conversion_system_obj.system_operation.get(end_use=end_use)
                .series_related_to.get(
                    thematic_description=thematic_description,
                    acquisition_method=acquisition_method,
                )
            )
            return {
                "time_series_object": time_series_object,
                "time_series_values": time_series_object.get_values(
                    start=start,
                    end=end,
                    mean=mean,
                    csv=csv,
                    workspace=workspace,
                    remote_path=remote_path,
                ),
            }
        except (
            IrregularTimeSeriesFile.DoesNotExist,
            AbstractEnergySystem.DoesNotExist,
        ):
            return {"time_series_object": None, "time_series_values": 0.0}


def add_time_series(
    values,
    thematic_description,
    acquisition_method,
    file_id,
    source,
    description=None,
    uom=None,
    end_use=None,
    energy_system=None,
    data_cleansing=False,
    csv=False,
    workspace=None,
    remote_path=None,
):
    """Documentation is missing."""
    time_series = IrregularTimeSeriesFile(
        objectclass=ObjectClass.objects.get(classname="IrregularTimeSeriesFile"),
        name="IrregularTimeSeriesFile_{}".format(file_id),
        gmlid="IrregularTimeSeriesFile_{}".format(file_id),
        thematic_description=thematic_description,
        acquisition_method=acquisition_method,
        file_id=file_id,
        uom=uom,
        source=source,
        description=description,
    )
    print(time_series.file_id)
    time_series.save()
    if csv is False:
        if data_cleansing:
            time_series.values = filter_outliers_invalid(values=values)
        else:
            time_series.values = values.dropna()

        if energy_system is None:
            pass
        else:

            time_series.series_related_to.add(
                energy_system.energy_conversion_system_obj.system_operation.get(
                    end_use=end_use
                )
            )

        try:
            time_series.save()
        except:
            time.sleep(30)
            try:
                time_series.save()
            except:
                print("--------------------------- ", file_id, " did not work")
    elif csv is True:
        if data_cleansing:
            values = filter_outliers_invalid(values=values)
        else:
            values = values.dropna()

        if energy_system is None:
            pass
        else:

            time_series.series_related_to.add(
                energy_system.energy_conversion_system_obj.system_operation.get(
                    end_use=end_use
                )
            )
            time_series.save()

        values.to_csv(os.path.join(workspace, file_id + ".csv"))
        try:
            owncloud.send_to_owncloud(
                local_path=os.path.join(workspace, file_id + ".csv"),
                remote_path=remote_path + file_id + ".csv",
            )
        except:
            time.sleep(30)
            try:
                owncloud.send_to_owncloud(
                    local_path=os.path.join(workspace, file_id + ".csv"),
                    remote_path=remote_path + file_id + ".csv",
                )
            except:
                print("--------------------------- ", file_id, " did not work")
    return time_series


def filter_outliers_invalid(values):
    results = values.copy()
    results.loc[:, "error"] = False
    results.loc[:, "q3"] = 9999.99
    results.loc[:, "q1"] = 0.0
    results.loc[:, "iqr"] = 0.0
    # 1. Drop nan values and find negative values
    results = results.dropna()
    # 2. Find constant values
    results.loc[:, "dx"] = results.iloc[:, 0].diff()
    results.loc[results["dx"].between(-0.001, 0.001), "error"] = True

    # 3. Find outliers
    results.loc[:, "day"] = results.index.dayofyear
    results.loc[:, "year"] = results.index.year

    for year in results.index.year.drop_duplicates(keep="first"):
        for day in results.index.dayofyear.drop_duplicates(keep="first"):
            results.loc[
                (results.day == day)
                & (results.year == year)
                & (results.error == False),
                "q3",
            ] = (
                results[
                    (results.day == day)
                    & (results.year == year)
                    & (results.error == False)
                ]
                .iloc[:, 0]
                .quantile(0.75)
            )
            results.loc[
                (results.day == day)
                & (results.year == year)
                & (results.error == False),
                "q1",
            ] = (
                results[
                    (results.day == day)
                    & (results.year == year)
                    & (results.error == False)
                ]
                .iloc[:, 0]
                .quantile(0.25)
            )

    results.loc[:, "iqr"] = results["q3"] - results["q1"]
    results.loc[
        results.iloc[:, 0].gt(results["q3"] + 3 * results["iqr"]), "error"
    ] = True
    results.loc[
        results.iloc[:, 0].lt(results["q3"] - 3 * results["iqr"]), "error"
    ] = True

    # 4. zero values are no outliers
    results.loc[results.iloc[:, 0] < 0, results.columns[0]] = 0.0
    results.loc[results.iloc[:, 0] == 0, "error"] = False
    results.loc[results.error == True, results.columns[0]] = np.nan
    results = results.drop(["error", "q3", "q1", "iqr", "dx", "day", "year"], axis=1)
    results = results.dropna()
    return results


def rolling_median(time_series_values, horizon="12h", threshold=20):
    """Detect and delete outliers, replace deleted data with rolling median

    This function detects outliers that are above a certain value. This values is
    calculated using the median of the whole time series and the given threshold
    (default=50). The outliers are deleted and replaced by a rolling median with given
    time horizon (default=12h). This will only influence periods where outliers are detected.

    Note, that the horizon will have an impact on your time series, large time horizons
    will lead to  unwanted dynamics (e.g. a value that is not in the same trend), small
    horizons may ne efficiently wipe your outliers. The horizon needs to be chosen
    depending on you time series time scale.

    This function is helpful if you have a large number of outliers that may also occur
    consecutive to each other. If you only have single outliers you might want to use
    function interpolate_median().

    Parameters
    ----------
    time_series_values : pd.DataFrame
        Pandas DataFrame with measured or simulated data.
    threshold : float
        Factor to be multiplied by median. Above this product all values
        are considered to be non-valid. Default is 50.
    horizon : string
        String that can be interpreted by pandas for time scale, e.g.:
            '15min': 15 minutes
            '30min': 30 minutes
            '1h': 1 hour
            ...
    Returns
    -------
    time_series_values : pandas.DataFrame
        DataFrame with measured data, where rolling median was applied.
    """
    time_series_values[
        time_series_values > threshold * time_series_values.median()
    ] = time_series_values.rolling(window=horizon, center=False).median()

    return time_series_values


def find_sim_without_res(city_model):
    """doc missing"""

    bldgs = bd_short.get_all_buildings(city_model)
    bldg_no_results = []
    for bldg in bldgs:
        ts_object = get_time_series_object(
            building=bldg,
            end_use="spaceHeating",
            thematic_description="Power",
            acquisition_method="simulation",
        )

        if ts_object is None:
            bldg_no_results.append(bldg)
    return bldg_no_results


def find_sim_without_res_series(city_model, ahu):
    """doc missing"""

    bldgs = bd_short.get_all_buildings(city_model)
    bldg_no_results = []
    for bldg in bldgs:
        try:
            if ahu is True:
                ts_object = get_time_series_data(
                    building=bldg,
                    end_use="ventilationHeating",
                    thematic_description="Power",
                    acquisition_method="simulation",
                    mean="365d",
                )
                if ts_object is None:
                    bldg_no_results.append(bldg)

            ts_object = get_time_series_data(
                building=bldg,
                end_use="spaceHeating",
                thematic_description="Power",
                acquisition_method="simulation",
                mean="365d",
            )
            if ts_object is None:
                bldg_no_results.append(bldg)
        except KeyError:
            if ahu is True:
                ts_object = get_time_series_object(
                    building=bldg,
                    end_use="spaceHeating",
                    thematic_description="Power",
                    acquisition_method="simulation",
                )
                bldg_no_results.append(bldg)
                if ts_object is None:
                    pass
                else:
                    ts_object.delete()

            ts_object = get_time_series_object(
                building=bldg,
                end_use="spaceHeating",
                thematic_description="Power",
                acquisition_method="simulation",
            )
            bldg_no_results.append(bldg)
            if ts_object is None:
                pass
            else:
                ts_object.delete()
    return list(set(bldg_no_results))
