BEGIN;

  --
  CREATE TABLE data_sonic_201701(
  CONSTRAINT __data_sonic_201701_check
  CHECK(valid > '2017-01-01 00:00+00'::timestamptz
        and valid <= '2017-02-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201701_idx on data_sonic_201701(tower, valid);
  GRANT ALL on data_sonic_201701 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201701 to tt_web;

  --
  CREATE TABLE data_analog_201701(
  CONSTRAINT __data_analog_201701_check
  CHECK(valid > '2017-01-01 00:00+00'::timestamptz
        and valid <= '2017-02-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201701_idx on data_analog_201701(tower, valid);
  GRANT ALL on data_analog_201701 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201701 to tt_web;
  

  --
  CREATE TABLE data_sonic_201702(
  CONSTRAINT __data_sonic_201702_check
  CHECK(valid > '2017-02-01 00:00+00'::timestamptz
        and valid <= '2017-03-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201702_idx on data_sonic_201702(tower, valid);
  GRANT ALL on data_sonic_201702 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201702 to tt_web;

  --
  CREATE TABLE data_analog_201702(
  CONSTRAINT __data_analog_201702_check
  CHECK(valid > '2017-02-01 00:00+00'::timestamptz
        and valid <= '2017-03-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201702_idx on data_analog_201702(tower, valid);
  GRANT ALL on data_analog_201702 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201702 to tt_web;
  

  --
  CREATE TABLE data_sonic_201703(
  CONSTRAINT __data_sonic_201703_check
  CHECK(valid > '2017-03-01 00:00+00'::timestamptz
        and valid <= '2017-04-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201703_idx on data_sonic_201703(tower, valid);
  GRANT ALL on data_sonic_201703 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201703 to tt_web;

  --
  CREATE TABLE data_analog_201703(
  CONSTRAINT __data_analog_201703_check
  CHECK(valid > '2017-03-01 00:00+00'::timestamptz
        and valid <= '2017-04-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201703_idx on data_analog_201703(tower, valid);
  GRANT ALL on data_analog_201703 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201703 to tt_web;
  

  --
  CREATE TABLE data_sonic_201704(
  CONSTRAINT __data_sonic_201704_check
  CHECK(valid > '2017-04-01 00:00+00'::timestamptz
        and valid <= '2017-05-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201704_idx on data_sonic_201704(tower, valid);
  GRANT ALL on data_sonic_201704 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201704 to tt_web;

  --
  CREATE TABLE data_analog_201704(
  CONSTRAINT __data_analog_201704_check
  CHECK(valid > '2017-04-01 00:00+00'::timestamptz
        and valid <= '2017-05-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201704_idx on data_analog_201704(tower, valid);
  GRANT ALL on data_analog_201704 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201704 to tt_web;
  

  --
  CREATE TABLE data_sonic_201705(
  CONSTRAINT __data_sonic_201705_check
  CHECK(valid > '2017-05-01 00:00+00'::timestamptz
        and valid <= '2017-06-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201705_idx on data_sonic_201705(tower, valid);
  GRANT ALL on data_sonic_201705 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201705 to tt_web;

  --
  CREATE TABLE data_analog_201705(
  CONSTRAINT __data_analog_201705_check
  CHECK(valid > '2017-05-01 00:00+00'::timestamptz
        and valid <= '2017-06-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201705_idx on data_analog_201705(tower, valid);
  GRANT ALL on data_analog_201705 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201705 to tt_web;
  

  --
  CREATE TABLE data_sonic_201706(
  CONSTRAINT __data_sonic_201706_check
  CHECK(valid > '2017-06-01 00:00+00'::timestamptz
        and valid <= '2017-07-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201706_idx on data_sonic_201706(tower, valid);
  GRANT ALL on data_sonic_201706 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201706 to tt_web;

  --
  CREATE TABLE data_analog_201706(
  CONSTRAINT __data_analog_201706_check
  CHECK(valid > '2017-06-01 00:00+00'::timestamptz
        and valid <= '2017-07-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201706_idx on data_analog_201706(tower, valid);
  GRANT ALL on data_analog_201706 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201706 to tt_web;
  

  --
  CREATE TABLE data_sonic_201707(
  CONSTRAINT __data_sonic_201707_check
  CHECK(valid > '2017-07-01 00:00+00'::timestamptz
        and valid <= '2017-08-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201707_idx on data_sonic_201707(tower, valid);
  GRANT ALL on data_sonic_201707 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201707 to tt_web;

  --
  CREATE TABLE data_analog_201707(
  CONSTRAINT __data_analog_201707_check
  CHECK(valid > '2017-07-01 00:00+00'::timestamptz
        and valid <= '2017-08-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201707_idx on data_analog_201707(tower, valid);
  GRANT ALL on data_analog_201707 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201707 to tt_web;
  

  --
  CREATE TABLE data_sonic_201708(
  CONSTRAINT __data_sonic_201708_check
  CHECK(valid > '2017-08-01 00:00+00'::timestamptz
        and valid <= '2017-09-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201708_idx on data_sonic_201708(tower, valid);
  GRANT ALL on data_sonic_201708 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201708 to tt_web;

  --
  CREATE TABLE data_analog_201708(
  CONSTRAINT __data_analog_201708_check
  CHECK(valid > '2017-08-01 00:00+00'::timestamptz
        and valid <= '2017-09-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201708_idx on data_analog_201708(tower, valid);
  GRANT ALL on data_analog_201708 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201708 to tt_web;
  

  --
  CREATE TABLE data_sonic_201709(
  CONSTRAINT __data_sonic_201709_check
  CHECK(valid > '2017-09-01 00:00+00'::timestamptz
        and valid <= '2017-10-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201709_idx on data_sonic_201709(tower, valid);
  GRANT ALL on data_sonic_201709 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201709 to tt_web;

  --
  CREATE TABLE data_analog_201709(
  CONSTRAINT __data_analog_201709_check
  CHECK(valid > '2017-09-01 00:00+00'::timestamptz
        and valid <= '2017-10-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201709_idx on data_analog_201709(tower, valid);
  GRANT ALL on data_analog_201709 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201709 to tt_web;
  

  --
  CREATE TABLE data_sonic_201710(
  CONSTRAINT __data_sonic_201710_check
  CHECK(valid > '2017-10-01 00:00+00'::timestamptz
        and valid <= '2017-11-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201710_idx on data_sonic_201710(tower, valid);
  GRANT ALL on data_sonic_201710 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201710 to tt_web;

  --
  CREATE TABLE data_analog_201710(
  CONSTRAINT __data_analog_201710_check
  CHECK(valid > '2017-10-01 00:00+00'::timestamptz
        and valid <= '2017-11-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201710_idx on data_analog_201710(tower, valid);
  GRANT ALL on data_analog_201710 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201710 to tt_web;
  

  --
  CREATE TABLE data_sonic_201711(
  CONSTRAINT __data_sonic_201711_check
  CHECK(valid > '2017-11-01 00:00+00'::timestamptz
        and valid <= '2017-12-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201711_idx on data_sonic_201711(tower, valid);
  GRANT ALL on data_sonic_201711 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201711 to tt_web;

  --
  CREATE TABLE data_analog_201711(
  CONSTRAINT __data_analog_201711_check
  CHECK(valid > '2017-11-01 00:00+00'::timestamptz
        and valid <= '2017-12-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201711_idx on data_analog_201711(tower, valid);
  GRANT ALL on data_analog_201711 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201711 to tt_web;
  

  --
  CREATE TABLE data_sonic_201712(
  CONSTRAINT __data_sonic_201712_check
  CHECK(valid > '2017-12-01 00:00+00'::timestamptz
        and valid <= '2018-01-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201712_idx on data_sonic_201712(tower, valid);
  GRANT ALL on data_sonic_201712 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201712 to tt_web;

  --
  CREATE TABLE data_analog_201712(
  CONSTRAINT __data_analog_201712_check
  CHECK(valid > '2017-12-01 00:00+00'::timestamptz
        and valid <= '2018-01-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201712_idx on data_analog_201712(tower, valid);
  GRANT ALL on data_analog_201712 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201712 to tt_web;
  
COMMIT;
