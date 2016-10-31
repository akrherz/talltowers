# -*- coding: utf-8 -*-
"""
make plot of recent data from talltowers project, for display on website.

@author: joe
"""
import os
import sys
import json
import datetime
from dateutil import tz
import psycopg2
from pandas.io.sql import read_sql
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot.
import matplotlib.pyplot as plt  # NOPEP8
import matplotlib.dates as mdates  # NOPEP8
# get database credentials
CONFIG = json.load(open("../config/settings.json", 'r'))

site_list = ['hamilton', 'story']
hours_back = 300
hour_interval = 24  # period of "%H:%M" tickmarks in hours
plot_dir = CONFIG['plotsdir']

# === plot dictionary ===
plot_dict = {'Sonic R.H.': {
    'ffn_plot': "{}-sonic-RH.png",
    'Y-label': 'Relative Humidity [%]',
    'channels': ['BoardHumidity_5m', 'BoardHumidity_10m',
                 'BoardHumidity_20m', 'BoardHumidity_40m',
                 'BoardHumidity_80m', 'BoardHumidity_120m']},
             'Sonic Brd-Tmp': {
    'ffn_plot': "{}-sonic-board-temp.png",
    'Y-label': 'Temperature [C]',
    'channels': ['BoardTemp_5m', 'BoardTemp_10m', 'BoardTemp_20m',
                 'BoardTemp_40m', 'BoardTemp_80m', 'BoardTemp_120m']},
             'Sonic Pitch': {
    'ffn_plot': "{}-sonic-pitch.png",
    'Y-label': 'Sonic Anemometer Pitch [deg]',
    'channels': ['InclinePitch_5m', 'InclinePitch_10m', 'InclinePitch_20m',
                 'InclinePitch_40m', 'InclinePitch_80m', 'InclinePitch_120m']},
             'Sonic Roll': {
    'ffn_plot': "{}-sonic-roll.png",
    'Y-label': 'Sonic Anemometer Role [deg]',
    'channels': ['InclineRoll_5m', 'InclineRoll_10m', 'InclineRoll_20m',
                 'InclineRoll_40m', 'InclineRoll_80m', 'InclineRoll_120m']}
             }

for key, value in plot_dict.items():
    for siteid, site in enumerate(site_list):
        time_now = datetime.datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
        time_data_start = time_now - datetime.timedelta(hours=hours_back)
        # timestamps for plotting
        ts_query_utc = datetime.datetime.strftime(time_now,
                                                  "%d-%b-%y %H:%M UTC")
        ts_now_local = datetime.datetime.strftime(
            time_now.astimezone(tz.gettz('US/Central')), "%d-%b-%y %H:%M %Z")
        # =================== GET DATA FROM DATABASE =====================
        # create empty list to hold data from each channel
        dfs = []
        conn = psycopg2.connect(('host={hostname} dbname={dbname} '
                                 'user={dbuser} password={dbpass}'
                                 ).format(**CONFIG['webdbconn']))
        cols = ["avg(%s) as avg_%s" % (v, v) for v in value['channels']]
        cols = ", ".join(cols)
        df = read_sql("""
            SELECT date_trunc('minute', valid) as ts,
            """ + cols + """ from data_monitor WHERE
            tower = %s and valid between %s and %s
            GROUP by ts ORDER by ts ASC
            """, conn, params=(siteid, time_data_start, time_now),
                      index_col='ts')
        if len(df.index) > 0:
            # === PLOT ===
            fig, ax = plt.subplots(figsize=(17, 11))
            ts = df.index
            plotted = False
            for col in df:
                if not df[col].isnull().all():
                    plotted = True
                    ax.plot(ts, df[col].values, label=col)
            if not plotted:
                sys.exit()
            # set legend and titles
            lgnd = ax.legend(loc='best')
            plot_title = ("One minute average of last {} hours "
                          "of {} from {}"
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
            # ax.xaxis.set_minor_locator(
            #    mdates.HourLocator(interval=hour_interval))
            # ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.grid(True, which="minor")
            # format MINOR X-axis ticks & labels
            # ax.xaxis.set_major_locator(mdates.DayLocator())
            # ax.xaxis.set_major_formatter(
            #    mdates.DateFormatter('\n%d-%b\n%Y'))
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
