# -*- coding: utf-8 -*-
"""
make plot of recent data from talltowers project, for display on website.

@author: joe
"""

import os
import json
import datetime
from dateutil import tz
import psycopg2
from pandas.io.sql import read_sql
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates  # NOPEP8
from pyiem.plot.use_agg import plt
register_matplotlib_converters()

CONFIG = json.load(open("../config/settings.json", 'r'))

# === INPUTS ===

site_list = ['hamilton', 'story']
hours_back = 36
plot_dir = CONFIG['plotsdir']

# --- sonics ---
plot_dict = {'Cup Annos NW': {
    'ffn_plot': "{}-cups-NW.png",
    'Y-label': 'Wind Speed [m/s]',
    'channels': ['WS_5m_NW', 'WS_10m_NWht', 'WS_20m_NW', 'WS_40m_NWht',
                 'WS_80m_NW', 'WS_120m_NWht']},
             'Cup Annos S': {
    'ffn_plot': "{}-cups-S.png",
    'Y-label': 'Wind Speed [m/s]',
    'channels': ['WS_5m_S', 'WS_10m_S', 'WS_20m_S', 'WS_40m_S',
                 'WS_80m_S', 'WS_120m_S']},
             'Air Temp': {
    'ffn_plot': "{}-temps.png",
    'Y-label': 'Temperature [C]',
    'channels': ['AirTC_5m', 'AirTC_10m', 'AirTC_20m', 'AirTC_40m',
                 'AirTC_80m', 'AirTC_120m_1', 'AirTC_120m_2']},
             'Rel. Hum.': {
    'ffn_plot': "{}-RH.png",
    'Y-label': 'RH [%]',
    'channels': ['RH_5m', 'RH_10m', 'RH_20m', 'RH_40m', 'RH_80m',
                 'RH_120m_1', 'RH_120m_2']},
             }

for key, value in plot_dict.items():
    for siteid, site in enumerate(site_list):
        # =================== GET TIME &  TIME STRING ====================
        time_now = datetime.datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
        time_data_start = time_now - datetime.timedelta(hours=hours_back)
        # timestamps for plotting
        ts_query_utc = datetime.datetime.strftime(time_now,
                                                  "%d-%b-%y %H:%M UTC")
        ts_now_local = datetime.datetime.strftime(
            time_now.astimezone(tz.gettz('US/Central')), "%d-%b-%y %H:%M %Z")
        # =================== GET DATA FROM DATABASE =====================
        # creaee empty list to hold data from each channel
        dfs = []
        conn = psycopg2.connect(('host={hostname} dbname={dbname} '
                                 'user={dbuser} password={dbpass}'
                                 ).format(**CONFIG['webdbconn']))
        cols = ["avg(%s) as avg_%s" % (v, v) for v in value['channels']]
        cols = ", ".join(cols)
        df = read_sql("""
            SELECT date_trunc('minute', valid) as ts,
            """ + cols + """ from data_analog WHERE
            tower = %s and valid between %s and %s
            GROUP by ts ORDER by ts ASC
            """, conn, params=(siteid, time_data_start, time_now),
                      index_col='ts')
        if not df.empty:
            fig, ax = plt.subplots(figsize=(17, 11))
            # do not rely on Pandas.DataFrame.plot(), because it uses
            # differnet dates than
            #   matplotlib, and because matplot lib will be invoked to
            # customize this plo,
            #   keep it matplotlib thoughout.
            for col in df:
                if df[col].isnull().all():
                    continue
                ax.plot(df.index.values, df[col], label=col)
            # set legend and titles
            lgnd = ax.legend(loc='best')
            plot_title = ("One minute average of last {} hours of {} "
                          "from {}"
                          ).format(hours_back, key, site.upper())
            ax.set_title(plot_title, fontsize=22)
            # set texts with times
            fig.text(x=0.98, y=0.99,
                     s='   generated at   \n' + ts_now_local,
                     color='#888888', ha='right', va='top', fontsize=12)
            ts_db_last = df.index[-1].astimezone(
                tz.gettz('UTC')).strftime('%d-%b-%y %H:%M UTC')
            fig.text(x=0.98, y=0.01,
                     s=('newest data:' + ts_db_last +
                        '\nquery at: ' + ts_query_utc),
                     color='#888888', ha='right', va='bottom', fontsize=10)
            # set all tick parameters, e.g.
            ax.tick_params(axis='both', which='both', labelsize=16)
            # format Y-axis
            ax.yaxis.set_label_text(value['Y-label'])
            ax.yaxis.label.set_size(16)
            ax.yaxis.grid(True)
            # format X-axis labels
            ax.xaxis.set_label_text('Time [UTC]')
            ax.xaxis.label.set_size(16)
            # format MINOR X-axis ticks & labels
            lacator_working = ax.xaxis.get_minor_locator()
            ax.xaxis.set_minor_locator(mdates.HourLocator(interval=2))
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.grid(True, which="minor")
            # format MINOR X-axis ticks & labels
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(
                mdates.DateFormatter('\n%d-%b\n%Y'))
            plt.setp(ax.get_xticklabels(), rotation=0,
                     horizontalalignment='center')
            # clean & save
            fig.tight_layout()
        else:
            fig, ax = plt.subplots()
            textstr = "No Data returned\n   from query!"
            ax.text(0.2, 0.40, textstr, transform=ax.transAxes, fontsize=34)

        # save figure
        ffn_plot = os.path.join(plot_dir, value['ffn_plot'].format(site))
        fig.savefig(ffn_plot, format='png')
        plt.close()
