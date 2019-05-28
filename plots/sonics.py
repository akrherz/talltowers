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

# get database credentials
CONFIG = json.load(open("../config/settings.json", 'r'))


def main():
    """Go Main Go."""
    site_list = ['hamilton', 'story']
    hours_back = 36
    plot_dir = CONFIG['plotsdir']

    # === plot dictionary ===
    plot_dict = {"Sonic Temp": {
        'ffn_plot': "{}-sonic-TEMPS.png",
        'Y-label': 'Temperature [C]',
        'channels': [
            'Ts_5m', 'Ts_10m', 'Ts_20m', 'Ts_40m', 'Ts_80m', 'Ts_120m']},
                'Sonic Diag': {
        'ffn_plot': "{}-sonic-Diag.png",
        'Y-label': 'AVERAGE sonic anno diag code [n/a]',
        'channels': ['Diag_5m', 'Diag_10m', 'Diag_20m', 'Diag_40m',
                     'Diag_80m', 'Diag_120m']}
                }

    for key, value in plot_dict.items():
        for siteid, site in enumerate(site_list):
            time_now = datetime.datetime.utcnow().replace(
                tzinfo=tz.gettz('UTC'))
            time_data_start = time_now - datetime.timedelta(hours=hours_back)
            # timestamps for plotting
            ts_query_utc = datetime.datetime.strftime(
                time_now, "%d-%b-%y %H:%M UTC")
            ts_now_local = datetime.datetime.strftime(
                time_now.astimezone(tz.gettz('US/Central')),
                "%d-%b-%y %H:%M %Z")
            # =================== GET DATA FROM DATABASE =====================
            # creaee empty list to hold data from each channel
            conn = psycopg2.connect(('host={hostname} dbname={dbname} '
                                     'user={dbuser} password={dbpass}'
                                     ).format(**CONFIG['webdbconn']))
            cols = ["avg(%s) as avg_%s" % (v, v) for v in value['channels']]
            cols = ", ".join(cols)
            df = read_sql("""
                SELECT date_trunc('minute', valid) as ts,
                """ + cols + """ from data_sonic WHERE
                tower = %s and valid between %s and %s
                GROUP by ts ORDER by ts ASC
            """, conn, params=(siteid, time_data_start, time_now),
                          index_col='ts')
            if not df.empty:
                # === PLOT ===
                fig, ax = plt.subplots(figsize=(17, 11))
                ts = df.index.values
                for col in df:
                    ax.plot(ts, df[col].values, label=col)
                # set legend and titles
                ax.legend(loc='best')
                plot_title = (
                    "One minute average of last {} hours of {} from {}"
                ).format(hours_back, key, site.upper())
                ax.set_title(plot_title, fontsize=22)
                # set texts with times
                fig.text(
                    x=0.98, y=0.99,
                    s='   generated at   \n' + ts_now_local,
                    color='#888888', ha='right', va='top', fontsize=12)
                ts_db_last = df.index[-1].astimezone(
                    tz.gettz('UTC')).strftime('%d-%b-%y %H:%M UTC')
                fig.text(
                    x=0.98, y=0.01,
                    s=('newest data:' + ts_db_last + '\nquery at: ' +
                       ts_query_utc),
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
                ax.set_xlim(ts[0], ts[-1])
                # format MINOR X-axis ticks & labels
                ax.xaxis.set_minor_locator(
                    mdates.HourLocator(interval=2))  # every 2 hours
                ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.grid(True, which="minor")
                # format MINOR X-axis ticks & labels
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(
                    mdates.DateFormatter('\n%d-%b\n%Y'))
                plt.setp(
                    ax.get_xticklabels(), rotation=0,
                    horizontalalignment='center')
                # clean & save
                fig.tight_layout()
            else:
                fig, ax = plt.subplots()
                textstr = "No Data returned\n   from query!"
                ax.text(
                    0.2, 0.40, textstr, transform=ax.transAxes, fontsize=34)

            # save figure
            ffn_plot = os.path.join(plot_dir, value['ffn_plot'].format(site))
            fig.savefig(ffn_plot, format='png')
            plt.close()


if __name__ == '__main__':
    main()
