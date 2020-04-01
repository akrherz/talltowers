"""Rename the files in the consumed/ folder into a tree"""
from csi2pg import decode_filename
import sys
import glob
import os
import json


def main(argv):
    cfg = json.load(open("../config/settings.json"))
    # set consumed directory
    consumed_dir = os.path.join(cfg["dataroot"], "consumed")
    os.chdir(consumed_dir)
    for fn in glob.glob("*.bdat"):
        _, valid = decode_filename(fn, "")
        restingdir = "%s/%s" % (consumed_dir, valid.strftime("%Y/%m/%d"))
        restingfn = "%s_%s" % (valid.strftime("%Y%m%d%H%M"), fn)
        if not os.path.isdir(restingdir):
            os.makedirs(restingdir)
        os.rename(fn, "%s/%s" % (restingdir, restingfn))
        print("%s -> %s" % (fn, restingfn))


if __name__ == "__main__":
    main(sys.argv)
