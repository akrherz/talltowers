"""Create a monthly netcdf file with X minute windowed stats"""
from __future__ import print_function
import sys
import datetime
import json

import netCDF4
import pytz
import psycopg2.extras
from tqdm import tqdm
import numpy as np
from pyiem.util import utc

CONFIG = json.load(open("../config/settings.json", "r"))
PGCONN = psycopg2.connect(
    (
        "host={hostname} dbname={dbname} " "user={dbuser} password={dbpass}"
    ).format(**CONFIG["dbconn"])
)
DT1970 = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.utc)
ANALOG_VARS = [
    "ws_5m_s",
    "ws_5m_nw",
    "winddir_5m_s",
    "winddir_5m_nw",
    "rh_5m",
    "airtc_5m",
    "ws_10m_s",
    "ws_10m_nw",
    "winddir_10m_s",
    "winddir_10m_nw",
    "rh_10m",
    "airtc_10m",
    "bp_10m",
    "ws_20m_s",
    "ws_20m_nw",
    "winddir_20m_s",
    "winddir_20m_nw",
    "rh_20m",
    "airtc_20m",
    "ws_40m_s",
    "ws_40m_nw",
    "winddir_40m_s",
    "winddir_40m_nw",
    "rh_40m",
    "airtc_40m",
    "ws_80m_s",
    "ws_80m_nw",
    "winddir_80m_s",
    "winddir_80m_nw",
    "rh_80m",
    "airtc_80m",
    "bp_80m",
    "ws_120m_s",
    "ws_120m_nw",
    "winddir_120m_s",
    "winddir_120m_nw",
    "rh_120m_1",
    "rh_120m_2",
    "airtc_120m_1",
    "airtc_120m_2",
]


def create_netcdf(valid, window):
    """Generate the netcdf file"""
    nt = {
        "ETTI4": {"lat": 42.345831, "lon": -93.519442, "elevation": 356.849},
        "MCAI4": {"lat": 42.196692, "lon": -93.357193, "elevation": 344.314},
    }
    nextmonth = (valid + datetime.timedelta(days=35)).replace(day=1)
    timelen = (nextmonth - valid).days * (60 / window) * 24
    nc = netCDF4.Dataset(
        valid.strftime("analog" + str(window) + "min_%Y%m.nc"), "w"
    )
    nc.createDimension("time", timelen)
    nc.createDimension("station", 2)
    nc.createDimension("stationnamelen", 3)
    nc.createDimension("number", 1)
    nc.createDimension("bnds", 2)

    station = nc.createVariable("station", "c", ("station", "stationnamelen"))
    station[:] = ["ham", "sto"]

    lat = nc.createVariable(
        "latitude", np.double, ("station",), fill_value=1e37
    )
    lat.long_name = "Station Degrees N Latitude"
    lat.units = "deg"
    lat[0] = nt["ETTI4"]["lat"]
    lat[1] = nt["MCAI4"]["lat"]

    lon = nc.createVariable(
        "longitude", np.double, ("station",), fill_value=1e37
    )
    lon.long_name = "Station Degrees E Longitude"
    lon.units = "deg"
    lon[0] = nt["ETTI4"]["lon"]
    lon[1] = nt["MCAI4"]["lon"]

    elev = nc.createVariable(
        "elevation", np.double, ("station",), fill_value=1e37
    )
    elev.long_name = "Approximate Station Base Elevation"
    elev.units = "m"
    elev[0] = nt["ETTI4"]["elevation"]
    elev[1] = nt["MCAI4"]["elevation"]

    bt = nc.createVariable("base_time", np.int, ("number",))
    bt.units = "seconds since 1970-01-01 00:00:00.000"
    bt[0] = (valid - DT1970).total_seconds()

    tm = nc.createVariable("time", np.double, ("time",))
    tm.units = "seconds since %s:00.000" % (valid.strftime("%Y-%m-%d %H:%M"),)
    tm.bounds = "time_bnds"
    # Start at 60 * window seconds in
    tm[:] = np.arange(60 * window, timelen * 60 * window + 1, 60 * window)

    tmb = nc.createVariable("time_bnds", "d", ("time", "bnds"))
    tmb[:, 0] = np.arange(0, timelen * 60 * window, 60 * window)
    tmb[:, 1] = np.arange(60 * window, timelen * 60 * window + 1, 60 * window)

    # analog data
    for vname in ANALOG_VARS:
        for stat in [
            "mean",
            "median",
            "minimum",
            "maximum",
            "standard_deviation",
            "median_abs_deviation",
            "count",
        ]:
            _vname = "%s_%s" % (vname, stat)
            ncvar = nc.createVariable(
                _vname, np.double, ("station", "time"), fill_value=1e37
            )
            units = "m/s"
            if vname.startswith("winddir_"):
                units = "deg"
            elif vname.startswith("rh_"):
                units = "%"
            elif vname.startswith("airtc_"):
                units = "C"
            elif vname.startswith("bp_"):
                units = "hPa"
            ncvar.units = units
            ncvar.long_name = vname
            ncvar.cell_methods = "time: %s" % (stat,)

    nc.sync()
    print("Done with netcdf definition")
    return nc


def dd(s):
    """Debug print statement with timestamp"""
    print("%s %s" % (datetime.datetime.utcnow(), s))


def xlate(vname):
    """Translate"""
    if vname in ["ws_10m_nw", "ws_40m_nw", "ws_120m_nw"]:
        return vname + "ht"
    return vname


def write_analog_data(valid, nc, window):
    """write data please"""
    table = valid.strftime("%Y%m")
    print("Querying data_analog...")
    # add bogus tower to query to get index goodness
    medsql = [
        ("median(%(v)s::numeric) as %(v)s_median") % dict(v=xlate(v))
        for v in ANALOG_VARS
    ]
    medsql = ", ".join(medsql)
    lgsql = [
        (
            "avg(%(v)s) as %(v)s_mean,\n"
            "median(%(v)s::numeric) as %(v)s_median,\n"
            "min(%(v)s) as %(v)s_minimum,\n"
            "max(%(v)s) as %(v)s_maximum,\n"
            "stddev(%(v)s) as %(v)s_standard_deviation,\n"
            "median(abs(%(v)s - "
            "%(v)s_median)::numeric) as %(v)s_median_abs_deviation,\n"
            "sum(case when %(v)s is not null then 1 else 0 end) as %(v)s_count\n"
        )
        % dict(v=xlate(v))
        for v in ANALOG_VARS
    ]
    lgsql = ", ".join(lgsql)

    cursor = PGCONN.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    for i, tstep in enumerate(
        tqdm(nc.variables["time"][:], disable=(not sys.stdout.isatty()))
    ):
        ets = valid + datetime.timedelta(seconds=tstep)
        sts = ets - datetime.timedelta(seconds=window * 60)
        cursor.execute(
            """
        WITH meds as (
            SELECT tower, """
            + medsql
            + """
            from data_analog_"""
            + table
            + """
            where valid >= %s and valid < %s and tower in (0, 1)
            GROUP by tower
        )
        SELECT a.tower,
            """
            + lgsql
            + """
            from data_analog_"""
            + table
            + """ a JOIN meds m
            on (a.tower = m.tower)
            where valid >= %s and valid < %s and a.tower in (0, 1)
            GROUP by a.tower
        """,
            (sts, ets, sts, ets),
        )
        # Compute some necessary things
        for row in cursor:
            for col in row:
                if col in ["tower", "valid", "delta"]:
                    continue
                nc.variables[col.replace("nwht", "nw")][row["tower"], i] = row[
                    col
                ]


def do(valid, window):
    """Workflow"""
    nc = create_netcdf(valid, window)
    write_analog_data(valid, nc, window)
    nc.close()


def main(argv):
    """Run"""
    valid = datetime.datetime(int(argv[2]), int(argv[3]), 1)
    valid = utc(valid.year, valid.month, valid.day)
    do(valid, int(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
