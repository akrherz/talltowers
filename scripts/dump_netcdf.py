"""Generate a standard netcdf file with the tall towers data!"""
import sys
import datetime
import netCDF4
import json
import pytz
import psycopg2
from tqdm import tqdm
import numpy as np
from pandas.io.sql import read_sql

CONFIG = json.load(open("../config/settings.json", 'r'))
PGCONN = psycopg2.connect(('host={hostname} dbname={dbname} '
                           'user={dbuser} password={dbpass}'
                           ).format(**CONFIG['dbconn']))
DT1970 = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.utc)


def create_netcdf(valid):
    """Generate the netcdf file"""
    nt = {'ETTI4': {'lat': 42.345831, 'lon': -93.519442, 'elevation': 356.849},
          'MCAI4': {'lat': 42.196692, 'lon': -93.357193, 'elevation': 344.314}}
    nc = netCDF4.Dataset(valid.strftime("tt%Y%m%d%H%M.nc"), 'w')
    nc.createDimension('time', 14400)
    nc.createDimension('station', 2)
    nc.createDimension('stationnamelen', 3)
    nc.createDimension('number', 1)
    nc.createDimension('sample', 20)

    station = nc.createVariable('station', 'c', ('station',
                                                 'stationnamelen'))
    station[:] = ['ham', 'sto']

    lat = nc.createVariable('latitude', np.double, ('station',),
                            fill_value=1e37)
    lat.long_name = 'Station Degrees N Latitude'
    lat.units = 'deg'
    lat[0] = nt['ETTI4']['lat']
    lat[1] = nt['MCAI4']['lat']

    lon = nc.createVariable('longitude', np.double, ('station',),
                            fill_value=1e37)
    lon.long_name = 'Station Degrees E Longitude'
    lon.units = 'deg'
    lon[0] = nt['ETTI4']['lon']
    lon[1] = nt['MCAI4']['lon']

    elev = nc.createVariable('elevation', np.double, ('station',),
                             fill_value=1e37)
    elev.long_name = 'Approximate Station Base Elevation'
    elev.units = 'm'
    elev[0] = nt['ETTI4']['elevation']
    elev[1] = nt['MCAI4']['elevation']

    bt = nc.createVariable('base_time', np.int, ('number',))
    bt.units = 'seconds since 1970-01-01 00:00:00.000'
    bt[0] = (valid - DT1970).total_seconds()

    tm = nc.createVariable('time', np.double, ('time',))
    tm.units = "seconds since %s:00.000" % (valid.strftime("%Y-%m-%d %H:%M"),)
    tm.interval = "1.000"
    tm[:] = np.arange(60*60*4)

    # sonic data
    for level in [5, 10, 20, 40, 80, 120]:
        for vname, unit in zip(['diag', 'ts', 'u', 'v', 'w'],
                               ['unitless', 'C', 'm/s', 'm/s', 'm/s']):
            vn = "%s_%sm" % (vname, level)
            v = nc.createVariable(vn, np.double, ('time', 'sample', 'station'),
                                  fill_value=1e37)
            v.long_name = "%s %sm %s" % (vname, level, unit)
            v.units = unit

    # analog data
    for vname in ['ws_5m_s', 'ws_5m_nw', 'winddir_5m_s', 'winddir_5m_nw',
                  'rh_5m', 'airtc_5m', 'ws_10m_s', 'ws_10m_nw',
                  'winddir_10m_s', 'winddir_10m_nw', 'rh_10m', 'airtc_10m',
                  'bp_10m', 'ws_20m_s', 'ws_20m_nw', 'winddir_20m_s',
                  'winddir_20m_nw', 'rh_20m', 'airtc_20m', 'ws_40m_s',
                  'ws_40m_nw', 'winddir_40m_s', 'winddir_40m_nw',
                  'rh_40m', 'airtc_40m', 'ws_80m_s', 'ws_80m_nw',
                  'winddir_80m_s', 'winddir_80m_nw', 'rh_80m', 'airtc_80m',
                  'bp_80m', 'ws_120m_s', 'ws_120m_nw', 'winddir_120m_s',
                  'winddir_120m_nw', 'rh_120m_1', 'rh_120m_2', 'airtc_120m_1',
                  'airtc_120m_2']:
        v = nc.createVariable(vname, np.double, ('time', 'station'),
                              fill_value=1e37)
        units = "m/s"
        if vname.startswith('winddir_'):
            units = 'deg'
        elif vname.startswith('rh_'):
            units = '%'
        elif vname.startswith('airtc_'):
            units = 'C'
        elif vname.startswith('bp_'):
            units = 'hPa'
        v.units = units
        v.long_name = vname

    nc.sync()
    print("Done with netcdf definition")
    return nc


def dd(s):
    print("%s %s" % (datetime.datetime.utcnow(), s))


def write_sonic_data(valid, nc):
    """write data please"""
    table = valid.strftime("%Y%m")
    print("Querying data_sonic....")
    # add bogus tower to query to get index goodness
    df = read_sql("""
        SELECT * from data_sonic_""" + table + """
        where valid >= %s and valid < %s and tower in (0, 1)
    """, PGCONN, params=(valid, valid + datetime.timedelta(hours=4)),
                  index_col=None)
    # Compute some necessary things
    df['delta'] = (df['valid'] - valid) / np.timedelta64(1, 's')
    df['sample'] = ((df['delta'] * 100) - (df['delta'].astype('i') * 100)) / 5
    xref = {'uz': 'w', 'ux': 'u', 'uy': 'v'}
    print("Writing data_sonic....")
    for col in tqdm(df.columns):
        if col in ['tower', 'valid', 'delta', 'sample']:
            continue
        v = col.split("_")[0]
        vname = col.replace(v, xref.get(v, v))
        data = np.ones(nc.variables[vname].shape, np.double) * 1e37
        for row in df[['tower', 'delta', 'sample', col]].itertuples():
            data[int(row[2]), row[3], row[1]] = row[4]
        nc.variables[vname][:] = data


def write_analog_data(valid, nc):
    """write data please"""
    table = valid.strftime("%Y%m")
    print("Querying data_analog...")
    # add bogus tower to query to get index goodness
    df = read_sql("""
        SELECT * from data_analog_""" + table + """
        where valid >= %s and valid < %s and tower in (0, 1)
    """, PGCONN, params=(valid, valid + datetime.timedelta(hours=4)),
                  index_col=None)
    # Compute some necessary things
    df['delta'] = (df['valid'] - valid) / np.timedelta64(1, 's')
    print("writing data_analog...")
    for col in tqdm(df.columns):
        if col in ['tower', 'valid', 'delta']:
            continue
        data = np.ones(nc.variables[col.replace("nwht", "nw")].shape,
                       np.double) * 1e37
        for row in df[['tower', 'delta', col]].itertuples():
            data[int(row[2]), row[1]] = row[3]
        nc.variables[col.replace("nwht", "nw")][:] = data


def do(valid):
    """Workflow"""
    nc = create_netcdf(valid)
    write_sonic_data(valid, nc)
    write_analog_data(valid, nc)
    nc.close()


def main(argv):
    """Run"""
    valid = datetime.datetime(int(argv[1]), int(argv[2]), int(argv[3]),
                              int(argv[4]), 0)
    valid = valid.replace(tzinfo=pytz.utc)
    do(valid)

if __name__ == '__main__':
    main(sys.argv)
