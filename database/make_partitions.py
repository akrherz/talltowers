import datetime

now = datetime.datetime(2017, 1, 1)
ets = datetime.datetime(2018, 1, 1)
print 'BEGIN;'
while now < ets:
    now = now.replace(day=1)
    nextmonth = (now + datetime.timedelta(days=32)).replace(day=1)
    d = {'d': now.strftime("%Y%m"),
         'this': now.strftime("%Y-%m-%d"),
         'next': nextmonth.strftime("%Y-%m-%d")}
    print """
  --
  CREATE TABLE data_sonic_%(d)s(
  CONSTRAINT __data_sonic_%(d)s_check
  CHECK(valid > '%(this)s 00:00+00'::timestamptz
        and valid <= '%(next)s 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_%(d)s_idx on data_sonic_%(d)s(tower, valid);
  GRANT ALL on data_sonic_%(d)s to tt_script,tt_admin;
  GRANT SELECT on data_sonic_%(d)s to tt_web;

  --
  CREATE TABLE data_analog_%(d)s(
  CONSTRAINT __data_analog_%(d)s_check
  CHECK(valid > '%(this)s 00:00+00'::timestamptz
        and valid <= '%(next)s 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_%(d)s_idx on data_analog_%(d)s(tower, valid);
  GRANT ALL on data_analog_%(d)s to tt_script,tt_admin;
  GRANT SELECT on data_analog_%(d)s to tt_web;
  """ % d
    now = nextmonth
print 'COMMIT;'
