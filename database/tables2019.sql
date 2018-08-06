BEGIN;

  --
  CREATE TABLE data_sonic_201901(
  CONSTRAINT __data_sonic_201901_check
  CHECK(valid > '2019-01-01 00:00+00'::timestamptz
        and valid <= '2019-02-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201901_idx on data_sonic_201901(tower, valid);
  GRANT ALL on data_sonic_201901 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201901 to tt_web;

  --
  CREATE TABLE data_analog_201901(
  CONSTRAINT __data_analog_201901_check
  CHECK(valid > '2019-01-01 00:00+00'::timestamptz
        and valid <= '2019-02-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201901_idx on data_analog_201901(tower, valid);
  GRANT ALL on data_analog_201901 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201901 to tt_web;
  

  --
  CREATE TABLE data_sonic_201902(
  CONSTRAINT __data_sonic_201902_check
  CHECK(valid > '2019-02-01 00:00+00'::timestamptz
        and valid <= '2019-03-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201902_idx on data_sonic_201902(tower, valid);
  GRANT ALL on data_sonic_201902 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201902 to tt_web;

  --
  CREATE TABLE data_analog_201902(
  CONSTRAINT __data_analog_201902_check
  CHECK(valid > '2019-02-01 00:00+00'::timestamptz
        and valid <= '2019-03-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201902_idx on data_analog_201902(tower, valid);
  GRANT ALL on data_analog_201902 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201902 to tt_web;
  

  --
  CREATE TABLE data_sonic_201903(
  CONSTRAINT __data_sonic_201903_check
  CHECK(valid > '2019-03-01 00:00+00'::timestamptz
        and valid <= '2019-04-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201903_idx on data_sonic_201903(tower, valid);
  GRANT ALL on data_sonic_201903 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201903 to tt_web;

  --
  CREATE TABLE data_analog_201903(
  CONSTRAINT __data_analog_201903_check
  CHECK(valid > '2019-03-01 00:00+00'::timestamptz
        and valid <= '2019-04-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201903_idx on data_analog_201903(tower, valid);
  GRANT ALL on data_analog_201903 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201903 to tt_web;
  

  --
  CREATE TABLE data_sonic_201904(
  CONSTRAINT __data_sonic_201904_check
  CHECK(valid > '2019-04-01 00:00+00'::timestamptz
        and valid <= '2019-05-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201904_idx on data_sonic_201904(tower, valid);
  GRANT ALL on data_sonic_201904 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201904 to tt_web;

  --
  CREATE TABLE data_analog_201904(
  CONSTRAINT __data_analog_201904_check
  CHECK(valid > '2019-04-01 00:00+00'::timestamptz
        and valid <= '2019-05-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201904_idx on data_analog_201904(tower, valid);
  GRANT ALL on data_analog_201904 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201904 to tt_web;
  

  --
  CREATE TABLE data_sonic_201905(
  CONSTRAINT __data_sonic_201905_check
  CHECK(valid > '2019-05-01 00:00+00'::timestamptz
        and valid <= '2019-06-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201905_idx on data_sonic_201905(tower, valid);
  GRANT ALL on data_sonic_201905 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201905 to tt_web;

  --
  CREATE TABLE data_analog_201905(
  CONSTRAINT __data_analog_201905_check
  CHECK(valid > '2019-05-01 00:00+00'::timestamptz
        and valid <= '2019-06-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201905_idx on data_analog_201905(tower, valid);
  GRANT ALL on data_analog_201905 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201905 to tt_web;
  

  --
  CREATE TABLE data_sonic_201906(
  CONSTRAINT __data_sonic_201906_check
  CHECK(valid > '2019-06-01 00:00+00'::timestamptz
        and valid <= '2019-07-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201906_idx on data_sonic_201906(tower, valid);
  GRANT ALL on data_sonic_201906 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201906 to tt_web;

  --
  CREATE TABLE data_analog_201906(
  CONSTRAINT __data_analog_201906_check
  CHECK(valid > '2019-06-01 00:00+00'::timestamptz
        and valid <= '2019-07-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201906_idx on data_analog_201906(tower, valid);
  GRANT ALL on data_analog_201906 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201906 to tt_web;
  

  --
  CREATE TABLE data_sonic_201907(
  CONSTRAINT __data_sonic_201907_check
  CHECK(valid > '2019-07-01 00:00+00'::timestamptz
        and valid <= '2019-08-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201907_idx on data_sonic_201907(tower, valid);
  GRANT ALL on data_sonic_201907 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201907 to tt_web;

  --
  CREATE TABLE data_analog_201907(
  CONSTRAINT __data_analog_201907_check
  CHECK(valid > '2019-07-01 00:00+00'::timestamptz
        and valid <= '2019-08-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201907_idx on data_analog_201907(tower, valid);
  GRANT ALL on data_analog_201907 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201907 to tt_web;
  

  --
  CREATE TABLE data_sonic_201908(
  CONSTRAINT __data_sonic_201908_check
  CHECK(valid > '2019-08-01 00:00+00'::timestamptz
        and valid <= '2019-09-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201908_idx on data_sonic_201908(tower, valid);
  GRANT ALL on data_sonic_201908 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201908 to tt_web;

  --
  CREATE TABLE data_analog_201908(
  CONSTRAINT __data_analog_201908_check
  CHECK(valid > '2019-08-01 00:00+00'::timestamptz
        and valid <= '2019-09-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201908_idx on data_analog_201908(tower, valid);
  GRANT ALL on data_analog_201908 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201908 to tt_web;
  

  --
  CREATE TABLE data_sonic_201909(
  CONSTRAINT __data_sonic_201909_check
  CHECK(valid > '2019-09-01 00:00+00'::timestamptz
        and valid <= '2019-10-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201909_idx on data_sonic_201909(tower, valid);
  GRANT ALL on data_sonic_201909 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201909 to tt_web;

  --
  CREATE TABLE data_analog_201909(
  CONSTRAINT __data_analog_201909_check
  CHECK(valid > '2019-09-01 00:00+00'::timestamptz
        and valid <= '2019-10-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201909_idx on data_analog_201909(tower, valid);
  GRANT ALL on data_analog_201909 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201909 to tt_web;
  

  --
  CREATE TABLE data_sonic_201910(
  CONSTRAINT __data_sonic_201910_check
  CHECK(valid > '2019-10-01 00:00+00'::timestamptz
        and valid <= '2019-11-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201910_idx on data_sonic_201910(tower, valid);
  GRANT ALL on data_sonic_201910 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201910 to tt_web;

  --
  CREATE TABLE data_analog_201910(
  CONSTRAINT __data_analog_201910_check
  CHECK(valid > '2019-10-01 00:00+00'::timestamptz
        and valid <= '2019-11-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201910_idx on data_analog_201910(tower, valid);
  GRANT ALL on data_analog_201910 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201910 to tt_web;
  

  --
  CREATE TABLE data_sonic_201911(
  CONSTRAINT __data_sonic_201911_check
  CHECK(valid > '2019-11-01 00:00+00'::timestamptz
        and valid <= '2019-12-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201911_idx on data_sonic_201911(tower, valid);
  GRANT ALL on data_sonic_201911 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201911 to tt_web;

  --
  CREATE TABLE data_analog_201911(
  CONSTRAINT __data_analog_201911_check
  CHECK(valid > '2019-11-01 00:00+00'::timestamptz
        and valid <= '2019-12-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201911_idx on data_analog_201911(tower, valid);
  GRANT ALL on data_analog_201911 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201911 to tt_web;
  

  --
  CREATE TABLE data_sonic_201912(
  CONSTRAINT __data_sonic_201912_check
  CHECK(valid > '2019-12-01 00:00+00'::timestamptz
        and valid <= '2019-01-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201912_idx on data_sonic_201912(tower, valid);
  GRANT ALL on data_sonic_201912 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201912 to tt_web;

  --
  CREATE TABLE data_analog_201912(
  CONSTRAINT __data_analog_201912_check
  CHECK(valid > '2019-12-01 00:00+00'::timestamptz
        and valid <= '2020-01-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201912_idx on data_analog_201912(tower, valid);
  GRANT ALL on data_analog_201912 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201912 to tt_web;
  
COMMIT;
