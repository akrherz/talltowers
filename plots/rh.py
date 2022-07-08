import psycopg2
import matplotlib.pyplot as plt
from pandas.io.sql import read_sql
import datetime
import numpy as np
from scipy.interpolate import NearestNDInterpolator

pgconn = psycopg2.connect(
    host="talltowers-db.agron.iastate.edu",
    user="tt_web",
    database="talltowers",
)
v = "uz"
df = read_sql(
    """
 SELECT date_trunc('microsecond', valid) as ts, avg("""
    + v
    + """_5m) as avg_rh_5m,
 avg("""
    + v
    + """_10m) as avg_rh_10m, avg("""
    + v
    + """_20m) as avg_rh_20m,
 avg("""
    + v
    + """_40m) as avg_rh_40m,
 avg("""
    + v
    + """_80m) as avg_rh_80m, avg("""
    + v
    + """_120m) as avg_rh_120m
 from data_sonic WHERE tower = 0 and valid > '2017-05-01 00:00:00+00'
 and valid < '2017-05-01 02:00:00+00'
 GROUP by ts ORDER by ts ASC""",
    pgconn,
    index_col="ts",
)
print(len(df.index))
x = []
y = []
z = []
ts0 = df.index[0]
print(ts0)
for i, row in df.iterrows():
    for level in [5, 10, 20, 40, 80, 120]:
        x.append((i - ts0).total_seconds())
        y.append(level)
        v = row["avg_rh_%sm" % (level,)]
        z.append(v)

x = np.array(x)
y = np.array(y)
z = np.array(z)
(fig, ax) = plt.subplots(1, 1, figsize=(12, 6))


xi = np.linspace(min(x), max(x), 1000)
xticks = []
xticklabels = []
for xx in xi[::100]:
    ts = ts0 + datetime.timedelta(seconds=xx)
    xticks.append(xx)
    xticklabels.append(ts.strftime("%H:%M:%S"))
yi = np.linspace(0, 120, 10)
xi, yi = np.meshgrid(xi, yi)
nn = NearestNDInterpolator((x, y), z)
vals = nn(xi, yi)

res = ax.contourf(xi, yi, vals)
ax.set_xticks(xticks)
ax.set_xticklabels(xticklabels, rotation=15)
ax.grid()
ax.set_title("Story Tower - 11 Aug 2016 ~1140 UTC~ Sonic Vertical Wind Speed")
fig.colorbar(res, label="mps")
fig.savefig("test.png")
