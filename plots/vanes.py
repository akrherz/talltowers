# -*- coding: utf-8 -*-
"""
make plot of recent data from talltowers project, for display on website.

@author: joe
"""

import datetime
import json
import os

import matplotlib.dates as mdates  # NOPEP8
import psycopg2
from dateutil import tz
from pandas.io.sql import read_sql
from pandas.plotting import register_matplotlib_converters
from pyiem.plot.use_agg import plt

register_matplotlib_converters()
# get database credentials
CONFIG = json.load(open("../config/settings.json", "r"))


site_list = ["hamilton", "story"]
hours_back = 36
hour_interval = 2  # period of "%H:%M" tickmarks in hours
plot_dir = CONFIG["plotsdir"]

# === plot dictionary ===
plot_dict = {
    "vanes NW": {
        "ffn_plot": "{}-vane-NW.png",
        "Y-label": "Direction [deg]",
        "channels": [
            "WindDir_5m_NW",
            "WindDir_10m_NW",
            "WindDir_20m_NW",
            "WindDir_40m_NW",
            "WindDir_80m_NW",
            "WindDir_120m_NW",
        ],
    },
    "vanes S": {
        "ffn_plot": "{}-vane-S.png",
        "Y-label": "Direction [deg]",
        "channels": [
            "WindDir_5m_S",
            "WindDir_10m_S",
            "WindDir_20m_S",
            "WindDir_40m_S",
            "WindDir_80m_S",
            "WindDir_120m_S",
        ],
    },
}

for key, value in plot_dict.items():
    for siteid, site in enumerate(site_list):
        time_now = datetime.datetime.utcnow().replace(tzinfo=tz.gettz("UTC"))
        time_data_start = time_now - datetime.timedelta(hours=hours_back)
        # timestamps for plotting
        ts_query_utc = datetime.datetime.strftime(
            time_now, "%d-%b-%y %H:%M UTC"
        )
        ts_now_local = datetime.datetime.strftime(
            time_now.astimezone(tz.gettz("US/Central")), "%d-%b-%y %H:%M %Z"
        )
        # =================== GET DATA FROM DATABASE =====================
        # creaee empty list to hold data from each channel
        dfs = []
        conn = psycopg2.connect(
            (
                "host={hostname} dbname={dbname} "
                "user={dbuser} password={dbpass}"
            ).format(**CONFIG["webdbconn"])
        )
        cols = ["avg(%s) as avg_%s" % (v, v) for v in value["channels"]]
        cols = ", ".join(cols)
        df = read_sql(
            """
            SELECT date_trunc('minute', valid) as ts,
            """
            + cols
            + """ from data_analog WHERE
            tower = %s and valid between %s and %s
            GROUP by ts ORDER by ts ASC
            """,
            conn,
            params=(siteid, time_data_start, time_now),
            index_col="ts",
        )

        if not df.empty:
            # === PLOT ===
            fig, ax = plt.subplots(figsize=(17, 11))
            ts = df.index
            for col in df:
                ax.plot(ts, df[col], label=col)
            # set legend and titles
            lgnd = ax.legend(loc="best")
            plot_title = (
                "One minute average of last {} hours of {} " "from {}"
            ).format(hours_back, key, site.upper())
            ax.set_title(plot_title, fontsize=22)
            # set texts with times
            fig.text(
                x=0.98,
                y=0.99,
                s="   generated at   \n" + ts_now_local,
                color="#888888",
                ha="right",
                va="top",
                fontsize=12,
            )
            ts_db_last = (
                df.index[-1]
                .astimezone(tz.gettz("UTC"))
                .strftime("%d-%b-%y %H:%M UTC")
            )
            fig.text(
                x=0.98,
                y=0.01,
                s=(
                    "newest data:" + ts_db_last + "\nquery at: " + ts_query_utc
                ),
                color="#888888",
                ha="right",
                va="bottom",
                fontsize=10,
            )
            # set all tick parameters, e.g.
            ax.tick_params(axis="both", which="both", labelsize=16)
            # format Y-axis
            ax.yaxis.set_label_text(value["Y-label"])
            ax.yaxis.label.set_size(16)
            ax.yaxis.grid(True)
            ax.set_yticks(range(0, 361, 30))
            ax.set_ylim([0, 360])
            # format X-axis labels
            ax.xaxis.set_label_text("Time [UTC]")
            ax.xaxis.label.set_size(16)
            # format MINOR X-axis ticks & labels
            lacator_working = ax.xaxis.get_minor_locator()
            ax.xaxis.set_minor_locator(
                mdates.HourLocator(interval=hour_interval)
            )
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
            ax.xaxis.grid(True, which="minor")
            # format MINOR X-axis ticks & labels
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("\n%d-%b\n%Y"))
            plt.setp(
                ax.get_xticklabels(), rotation=0, horizontalalignment="center"
            )
            # clean & save
            fig.tight_layout()
        else:
            fig, ax = plt.subplots()
            textstr = "No Data returned\n   from query!"
            ax.text(0.2, 0.40, textstr, transform=ax.transAxes, fontsize=34)
        # save figure
        ffn_plot = os.path.join(plot_dir, value["ffn_plot"].format(site))
        fig.savefig(ffn_plot, format="png")
        plt.close()
