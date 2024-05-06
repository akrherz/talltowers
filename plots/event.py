# -*- coding: utf-8 -*-
"""
Very similar to pg-www-plot.py, but plots data from related channels,
at both sites, on one plot

make plot of recent data from talltowers project, for display on website.

@author: joe
"""

import matplotlib.dates as mdates  # NOPEP8
import matplotlib.pyplot as plt  # NOPEP8
import pandas as pd
import psycopg2
import pytz
from pandas.io.sql import read_sql

TZ = pytz.timezone("America/Chicago")


def get_data():
    conn = psycopg2.connect(
        database="talltowers",
        host="talltowers-db.agron.iastate.edu",
        user="tt_web",
    )

    df = read_sql(
        """
        SELECT * from data_analog WHERE
        valid between '2017-05-01 00:00+00' and '2017-05-01 02:00:00+00'
        and tower = 0 ORDER by valid ASC
        """,
        conn,
        index_col="valid",
    )
    df.to_csv("data.csv")


df = pd.read_csv("data.csv")
df["valid"] = pd.to_datetime(df["valid"])
df.set_index("valid", inplace=True)

fig, (ax, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
ax.plot(df.index.values, df["bp_10m"])
ax.set_title(
    (
        "ISU Atmospheric Observatory :: Hamilton County Tall Tower\n"
        "10 meter AGL 1hz data on evening of 30 April 2017"
    )
)
ax.set_ylabel("Air Pressure [mb]")
ax22 = ax2.twinx()
ax22.plot(df.index.values, df["ws_20m_s"], zorder=3)
ax2.scatter(df.index.values, df["winddir_20m_s"], color="r", zorder=2)
ax2.set_yticks(range(0, 361, 90))
ax2.set_yticklabels(["N", "E", "S", "W", "N"])
ax2.set_ylim(0, 360)
ax2.set_ylabel("Wind Direction", color="r")
ax22.set_ylim(0, 20)
ax22.set_yticks([0, 5, 10, 15, 20])
ax22.set_ylabel("Wind Speed [mps]", color="b")
# format MINOR X-axis ticks & labels
ax.xaxis.set_major_locator(
    mdates.MinuteLocator(byminute=[0, 15, 30, 45], tz=TZ)
)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%-I:%M %p", tz=TZ))
ax.grid(True)
ax2.grid(True)
ax2.set_xlabel("30 April 2017 (Central Daylight Time)")
# save figure
fig.savefig("test.png")
plt.close()
