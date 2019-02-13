# -*- coding: utf-8 -*-
"""
Very similar to pg-www-plot.py, but plots data from related channels,
at both sites, on one plot

make plot of recent data from talltowers project, for display on website.

@author: joe
"""
import os
import json
import datetime
from dateutil import tz
import psycopg2
from pandas.io.sql import read_sql
import matplotlib
matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot.
import matplotlib.pyplot as plt  # NOPEP8
import matplotlib.dates as mdates  # NOPEP8

CONFIG = json.load(open("../config/settings.json", 'r'))

# === INPUTS ===

site_list = ['hamilton', 'story']
hours_back = 36
plot_dir = CONFIG['plotsdir']

plot_dict = {'Air Pressure': {
    'ffn_plot': "both-Baro.png",
    'Y-label': 'Barometric Pressure [kPa]',
    'channels': ['BP_10m', 'BP_80m']}
}

for key, value in plot_dict.items():
    time_now = datetime.datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
    time_data_start = time_now - datetime.timedelta(hours=hours_back)
    # timestamps for plotting
    ts_query_utc = datetime.datetime.strftime(time_now, "%d-%b-%y %H:%M UTC")
    ts_now_local = datetime.datetime.strftime(
        time_now.astimezone(tz.gettz('US/Central')), "%d-%b-%y %H:%M %Z")
    dfs = []
    conn = psycopg2.connect(('host={hostname} dbname={dbname} '
                             'user={dbuser} password={dbpass}'
                             ).format(**CONFIG['webdbconn']))
    cols = ["avg(%s) as avg_%s" % (v, v) for v in value['channels']]
    cols = ", ".join(cols)
    df = read_sql("""
        SELECT tower, date_trunc('minute', valid) as ts,
        """ + cols + """ from data_analog WHERE
        valid between %s and %s
        GROUP by tower, ts ORDER by ts ASC
        """, conn, params=(time_data_start, time_now),
                  index_col=None)
    if len(df.index) > 0:
        # === PLOT ===
        fig, ax = plt.subplots(figsize=(17, 11))
        for siteid in [0, 1]:
            for col in value['channels']:
                df2 = df[df['tower'] == siteid]
                ax.plot(df2['ts'].values, df2["avg_" + col.lower()],
                        label="%s %s" % (site_list[siteid], col))
        # set legend and titles
        lgnd = ax.legend(loc='best')
        plot_title = ("One minute average of last {} hours of {} from BOTH"
                      ).format(hours_back, key)
        ax.set_title(plot_title, fontsize=22)
        # set texts with times
        fig.text(x=0.98, y=0.99, s='   generated at   \n' + ts_now_local,
                 color='#888888', ha='right', va='top', fontsize=12)
        ts_db_last = df.iloc[-1]['ts'].astimezone(
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
        ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%d-%b\n%Y'))
        plt.setp(ax.get_xticklabels(), rotation=0,
                 horizontalalignment='center')
        # clean & save
        fig.tight_layout()
    else:
        fig, ax = plt.subplots()
        textstr = "No Data returned\n   from query!"
        ax.text(0.2, 0.40, textstr, transform=ax.transAxes, fontsize=34)
    # save figure
    ffn_plot = os.path.join(plot_dir, value['ffn_plot'])
    fig.savefig(ffn_plot, format='png')
    plt.close()
