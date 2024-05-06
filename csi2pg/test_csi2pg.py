"""Test csi2pg."""

import datetime
import os

import pytz

import csi2pg

DATAROOT = os.path.join(os.path.dirname(__file__), "../examples")


def test_decode_filename():
    """Test filename decoding."""
    res, valid = csi2pg.decode_filename("hamSg8muk.bdat", DATAROOT)
    expected = ("%s/2016/08/22/ham_sonic_160822-1920") % (DATAROOT,)
    assert res == expected
    expected = datetime.datetime(2016, 8, 22, 19, 20).replace(tzinfo=pytz.utc)
    assert valid == expected


def test_bin2pg():
    """Can we process?"""
    consumed_dir = os.path.join(DATAROOT, "consumed")
    fns = ["hamSg8muk.bdat", "stoAg8muk.bdat"]
    csi2pg.bin2pg(DATAROOT, fns, consumed_dir, csi2pg.CONFIG["dbconn"])
    for fn in fns:
        for mydir in ["consumed/2016/08/22", "quarentine"]:
            d = os.path.join(DATAROOT, mydir)
            for f in ["", "201608221920_"]:
                oldfn = "%s/%s%s" % (d, f, fn)
                if os.path.isfile(oldfn):
                    stablefn = "%s/%s" % (DATAROOT, fn)
                    os.rename(oldfn, stablefn)
