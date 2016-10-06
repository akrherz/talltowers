import unittest
import csi2pg
import os
import pytz
import datetime

DATAROOT = os.path.join(os.path.dirname(__file__), "../examples")


class TestCase(unittest.TestCase):

    def test_decode_filename(self):
        res, valid = csi2pg.decode_filename('hamSg8muk.bdat', DATAROOT)
        expected = ("%s/2016/08/22/ham_sonic_160822-1920"
                    ) % (DATAROOT, )
        self.assertTrue(res == expected)
        expected = datetime.datetime(2016, 8, 22, 19, 20).replace(
            tzinfo=pytz.utc)
        self.assertEquals(valid, expected)

    def test_bin2pg(self):
        consumed_dir = os.path.join(DATAROOT, 'consumed')
        fns = ['hamSg8muk.bdat', 'stoAg8muk.bdat']
        res = csi2pg.bin2pg(DATAROOT, fns,
                            consumed_dir, csi2pg.CONFIG['dbconn'], False)
        for fn in fns:
            for mydir in ['consumed/2016/08/22', 'quarentine']:
                d = os.path.join(DATAROOT, mydir)
                for f in ['', '201608221920_']:
                    oldfn = "%s/%s%s" % (d, f, fn)
                    if os.path.isfile(oldfn):
                        stablefn = "%s/%s" % (DATAROOT, fn)
                        os.rename(oldfn, stablefn)
        self.assertTrue(res is None)
