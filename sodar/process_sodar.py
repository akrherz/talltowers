"""Process the SODAR files.

data starts 2018-05-24-17-40
cd 963/
-rw-rw-rw- triton_963_2018-07-31-16-50_extended.csv
-rw-rw-rw- triton_963_2018-07-31-16-50_operational.csv
-rw-rw-rw- triton_963_2018-07-31-16-50_standard.csv
"""
import re
import os
import sys
import datetime
import json
from ftplib import FTP_TLS

import pandas as pd
import pytz
import psycopg2

COLRE = re.compile("^(?P<elev>[0-9]+)m (?P<name>.*?)-?(?P<extra>[ABC])?$")
CONFIG = json.load(open("../config/settings.json", "r"))
PGCONN = psycopg2.connect(
    (
        "host={hostname} dbname={dbname} " "user={dbuser} password={dbpass}"
    ).format(**CONFIG["dbconn"])
)


def nice(val):
    """Make sure this value is nice"""
    if pd.isna(val):
        return None
    return val


def dbsave(df, valid):
    """Save to the database, a dataframe"""
    table = "sodar_profile" if "beamnum" in df.columns else "sodar_surface"
    cursor = PGCONN.cursor()
    cursor.execute(
        """
    DELETE from """
        + table
        + """ WHERE station = 963 and valid = %s
    """,
        (valid,),
    )
    if table == "sodar_surface":
        cols = ["station", "valid"]
        args = ["963", valid]
        row = df.iloc[0]
        for col in df.columns:
            args.append(nice(row[col]))
            cols.append(col)
        cols = ",".join(cols)
        vals = ",".join(["%s"] * len(args))
        cursor.execute(
            """
            INSERT into """
            + table
            + """("""
            + cols
            + """)
            VALUES ("""
            + vals
            + """)
        """,
            args,
        )
    else:
        for _, row in df.iterrows():
            cols = ["station", "valid"]
            args = ["963", valid]
            for col in df.columns:
                args.append(nice(row[col]))
                cols.append(col)
            cols = ",".join(cols)
            vals = ",".join(["%s"] * len(args))
            sql = (
                """
                INSERT into """
                + table
                + """("""
                + cols
                + """)
                VALUES ("""
                + vals
                + """)
            """
            )
            cursor.execute(sql, args)

    cursor.close()
    PGCONN.commit()


def strcol(col):
    """Regularize"""
    return col.lower().replace("-", "_").replace(" ", "_")


def translate_column(col):
    """Turn the column name into actionable stuff"""
    m = COLRE.match(col)
    if m is None:
        return [None, strcol(col), None]
    res = m.groupdict()
    return [res["elev"], strcol(res["name"]), res["extra"]]


def ingest(valid):
    """Process the files."""
    dfs = []
    for suffix in ["extended", "operational", "standard"]:
        fn = valid.strftime(
            "/home/sodar/triton_963_%Y-%m-%d-%H-%M_" + suffix + ".csv"
        )
        if not os.path.isfile(fn):
            print("process_sodar %s missing" % (fn,))
            continue
        try:
            df = pd.read_csv(fn)
        except Exception as exp:
            print("process_sodar reading %s resulted in exp %s" % (fn, exp))
            continue
        df.set_index(df.columns[0], inplace=True)
        dfs.append(df)
    if not dfs:
        return
    df = dfs[0].join(dfs[1:])
    surface = {}
    profiles = []
    for col in df.columns:
        res = translate_column(col)
        val = df.iloc[0][col]
        if res[0] is None:
            surface[res[1]] = val
        else:
            profiles.append(
                {
                    "labelin": "%s_%s"
                    % (res[0], res[2] if res[2] is not None else "0"),
                    "colname": res[1],
                    "value": val,
                }
            )
    profile = pd.DataFrame(profiles)
    profile2 = profile.pivot(
        index="labelin", values="value", columns="colname"
    )
    profile2.reset_index(inplace=True)
    profile2["height"] = profile2["labelin"].str.split("_").str.get(0)
    profile2["label"] = profile2["labelin"].str.split("_").str.get(1)
    profile2.drop("labelin", axis=1, inplace=True)
    dbsave(profile2, valid)
    surface = pd.DataFrame([surface])
    dbsave(surface, valid)


def download_files(valid, offset):
    """Get the files for this valid time."""
    settings = json.loads(open("secret.json").read())
    conn = None
    downloaded = 0
    for suffix in ["extended", "operational", "standard"]:
        remotefn = valid.strftime(
            "963/triton_963_%Y-%m-%d-%H-%M_" + suffix + ".csv"
        )
        localfn = "/home/sodar/%s" % (remotefn[4:],)
        if os.path.isfile(localfn):
            continue
        if conn is None:
            conn = FTP_TLS(settings["host"])
            conn.login(settings["username"], settings["password"])
            conn.prot_p()
        fp = open(localfn, "wb")
        try:
            conn.retrbinary("RETR %s" % (remotefn,), fp.write)
        except Exception as exp:
            if offset > 0:
                print("download of %s failed with %s" % (remotefn, exp))
            fp.close()
            os.unlink(localfn)
            continue
        fp.close()
        downloaded += 1
    if conn:
        conn.close()
    return downloaded


def main(argv):
    """Go Main"""
    valid = datetime.datetime(
        int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])
    )
    valid = valid.replace(tzinfo=pytz.UTC)
    for offset in [0, 1, 6, 24, 72]:
        valid2 = valid - datetime.timedelta(hours=offset)
        downloaded = download_files(valid2, offset)
        # Make sure we have a quorum
        if offset == 0 and downloaded == 3:
            ingest(valid2)
        # if previous times downloaded files, do that too
        elif offset > 0 and downloaded > 0:
            ingest(valid2)


if __name__ == "__main__":
    main(sys.argv)
