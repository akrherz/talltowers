BEGIN;

  --
  CREATE TABLE data_sonic_202001(
  CONSTRAINT __data_sonic_202001_check
  CHECK(valid > '2020-01-01 00:00+00'::timestamptz
        and valid <= '2020-02-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202001_idx on data_sonic_202001(tower, valid);
  GRANT ALL on data_sonic_202001 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202001 to tt_web;

  --
  CREATE TABLE data_analog_202001(
  CONSTRAINT __data_analog_202001_check
  CHECK(valid > '2020-01-01 00:00+00'::timestamptz
        and valid <= '2020-02-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202001_idx on data_analog_202001(tower, valid);
  GRANT ALL on data_analog_202001 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202001 to tt_web;
  

  --
  CREATE TABLE data_sonic_202002(
  CONSTRAINT __data_sonic_202002_check
  CHECK(valid > '2020-02-01 00:00+00'::timestamptz
        and valid <= '2020-03-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202002_idx on data_sonic_202002(tower, valid);
  GRANT ALL on data_sonic_202002 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202002 to tt_web;

  --
  CREATE TABLE data_analog_202002(
  CONSTRAINT __data_analog_202002_check
  CHECK(valid > '2020-02-01 00:00+00'::timestamptz
        and valid <= '2020-03-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202002_idx on data_analog_202002(tower, valid);
  GRANT ALL on data_analog_202002 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202002 to tt_web;
  

  --
  CREATE TABLE data_sonic_202003(
  CONSTRAINT __data_sonic_202003_check
  CHECK(valid > '2020-03-01 00:00+00'::timestamptz
        and valid <= '2020-04-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202003_idx on data_sonic_202003(tower, valid);
  GRANT ALL on data_sonic_202003 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202003 to tt_web;

  --
  CREATE TABLE data_analog_202003(
  CONSTRAINT __data_analog_202003_check
  CHECK(valid > '2020-03-01 00:00+00'::timestamptz
        and valid <= '2020-04-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202003_idx on data_analog_202003(tower, valid);
  GRANT ALL on data_analog_202003 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202003 to tt_web;
  

  --
  CREATE TABLE data_sonic_202004(
  CONSTRAINT __data_sonic_202004_check
  CHECK(valid > '2020-04-01 00:00+00'::timestamptz
        and valid <= '2020-05-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202004_idx on data_sonic_202004(tower, valid);
  GRANT ALL on data_sonic_202004 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202004 to tt_web;

  --
  CREATE TABLE data_analog_202004(
  CONSTRAINT __data_analog_202004_check
  CHECK(valid > '2020-04-01 00:00+00'::timestamptz
        and valid <= '2020-05-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202004_idx on data_analog_202004(tower, valid);
  GRANT ALL on data_analog_202004 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202004 to tt_web;
  

  --
  CREATE TABLE data_sonic_202005(
  CONSTRAINT __data_sonic_202005_check
  CHECK(valid > '2020-05-01 00:00+00'::timestamptz
        and valid <= '2020-06-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202005_idx on data_sonic_202005(tower, valid);
  GRANT ALL on data_sonic_202005 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202005 to tt_web;

  --
  CREATE TABLE data_analog_202005(
  CONSTRAINT __data_analog_202005_check
  CHECK(valid > '2020-05-01 00:00+00'::timestamptz
        and valid <= '2020-06-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202005_idx on data_analog_202005(tower, valid);
  GRANT ALL on data_analog_202005 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202005 to tt_web;
  

  --
  CREATE TABLE data_sonic_202006(
  CONSTRAINT __data_sonic_202006_check
  CHECK(valid > '2020-06-01 00:00+00'::timestamptz
        and valid <= '2020-07-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202006_idx on data_sonic_202006(tower, valid);
  GRANT ALL on data_sonic_202006 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202006 to tt_web;

  --
  CREATE TABLE data_analog_202006(
  CONSTRAINT __data_analog_202006_check
  CHECK(valid > '2020-06-01 00:00+00'::timestamptz
        and valid <= '2020-07-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202006_idx on data_analog_202006(tower, valid);
  GRANT ALL on data_analog_202006 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202006 to tt_web;
  

  --
  CREATE TABLE data_sonic_202007(
  CONSTRAINT __data_sonic_202007_check
  CHECK(valid > '2020-07-01 00:00+00'::timestamptz
        and valid <= '2020-08-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202007_idx on data_sonic_202007(tower, valid);
  GRANT ALL on data_sonic_202007 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202007 to tt_web;

  --
  CREATE TABLE data_analog_202007(
  CONSTRAINT __data_analog_202007_check
  CHECK(valid > '2020-07-01 00:00+00'::timestamptz
        and valid <= '2020-08-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202007_idx on data_analog_202007(tower, valid);
  GRANT ALL on data_analog_202007 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202007 to tt_web;
  

  --
  CREATE TABLE data_sonic_202008(
  CONSTRAINT __data_sonic_202008_check
  CHECK(valid > '2020-08-01 00:00+00'::timestamptz
        and valid <= '2020-09-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202008_idx on data_sonic_202008(tower, valid);
  GRANT ALL on data_sonic_202008 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202008 to tt_web;

  --
  CREATE TABLE data_analog_202008(
  CONSTRAINT __data_analog_202008_check
  CHECK(valid > '2020-08-01 00:00+00'::timestamptz
        and valid <= '2020-09-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202008_idx on data_analog_202008(tower, valid);
  GRANT ALL on data_analog_202008 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202008 to tt_web;
  

  --
  CREATE TABLE data_sonic_202009(
  CONSTRAINT __data_sonic_202009_check
  CHECK(valid > '2020-09-01 00:00+00'::timestamptz
        and valid <= '2020-10-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202009_idx on data_sonic_202009(tower, valid);
  GRANT ALL on data_sonic_202009 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202009 to tt_web;

  --
  CREATE TABLE data_analog_202009(
  CONSTRAINT __data_analog_202009_check
  CHECK(valid > '2020-09-01 00:00+00'::timestamptz
        and valid <= '2020-10-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202009_idx on data_analog_202009(tower, valid);
  GRANT ALL on data_analog_202009 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202009 to tt_web;
  

  --
  CREATE TABLE data_sonic_202010(
  CONSTRAINT __data_sonic_202010_check
  CHECK(valid > '2020-10-01 00:00+00'::timestamptz
        and valid <= '2020-11-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202010_idx on data_sonic_202010(tower, valid);
  GRANT ALL on data_sonic_202010 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202010 to tt_web;

  --
  CREATE TABLE data_analog_202010(
  CONSTRAINT __data_analog_202010_check
  CHECK(valid > '2020-10-01 00:00+00'::timestamptz
        and valid <= '2020-11-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202010_idx on data_analog_202010(tower, valid);
  GRANT ALL on data_analog_202010 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202010 to tt_web;
  

  --
  CREATE TABLE data_sonic_202011(
  CONSTRAINT __data_sonic_202011_check
  CHECK(valid > '2020-11-01 00:00+00'::timestamptz
        and valid <= '2020-12-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202011_idx on data_sonic_202011(tower, valid);
  GRANT ALL on data_sonic_202011 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202011 to tt_web;

  --
  CREATE TABLE data_analog_202011(
  CONSTRAINT __data_analog_202011_check
  CHECK(valid > '2020-11-01 00:00+00'::timestamptz
        and valid <= '2020-12-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202011_idx on data_analog_202011(tower, valid);
  GRANT ALL on data_analog_202011 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202011 to tt_web;
  

  --
  CREATE TABLE data_sonic_202012(
  CONSTRAINT __data_sonic_202012_check
  CHECK(valid > '2020-12-01 00:00+00'::timestamptz
        and valid <= '2021-01-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_202012_idx on data_sonic_202012(tower, valid);
  GRANT ALL on data_sonic_202012 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_202012 to tt_web;

  --
  CREATE TABLE data_analog_202012(
  CONSTRAINT __data_analog_202012_check
  CHECK(valid > '2020-12-01 00:00+00'::timestamptz
        and valid <= '2021-01-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_202012_idx on data_analog_202012(tower, valid);
  GRANT ALL on data_analog_202012 to tt_script,tt_admin;
  GRANT SELECT on data_analog_202012 to tt_web;
  
COMMIT;
