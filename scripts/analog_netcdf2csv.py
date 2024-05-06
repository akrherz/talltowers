"""Convert our fancy NetCDF file to CSV"""

from __future__ import print_function

import datetime
import sys

import netCDF4
import pandas as pd


def main(argv):
    """Our main function, horray"""
    filename = argv[1]
    nc = netCDF4.Dataset(filename)
    stations = netCDF4.chartostring(nc.variables["station"][:])
    basets = datetime.datetime.strptime(
        nc.variables["time"].units.split()[2], "%Y-%m-%d"
    )
    tindex = []
    for offset in nc.variables["time"][:]:
        tindex.append(basets + datetime.timedelta(seconds=offset))
    dfs = [
        pd.DataFrame(index=pd.Series(tindex, name="time")),
        pd.DataFrame(index=pd.Series(tindex, name="time")),
    ]
    for sid in range(nc.dimensions["station"].size):
        for vname in nc.variables:
            ncvar = nc.variables[vname][:]
            if ncvar.shape != (
                nc.dimensions["station"].size,
                nc.dimensions["time"].size,
            ):
                continue
            dfs[sid][vname] = ncvar[sid, :]
    dfs[0].to_csv("%s_%s.csv" % (stations[0], basets.strftime("%Y%m%d")))
    dfs[1].to_csv("%s_%s.csv" % (stations[1], basets.strftime("%Y%m%d")))


if __name__ == "__main__":
    main(sys.argv)
