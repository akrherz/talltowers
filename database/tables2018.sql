BEGIN;

  --
  CREATE TABLE data_sonic_201801(
  CONSTRAINT __data_sonic_201801_check
  CHECK(valid > '2018-01-01 00:00+00'::timestamptz
        and valid <= '2018-02-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201801_idx on data_sonic_201801(tower, valid);
  GRANT ALL on data_sonic_201801 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201801 to tt_web;

  --
  CREATE TABLE data_analog_201801(
  CONSTRAINT __data_analog_201801_check
  CHECK(valid > '2018-01-01 00:00+00'::timestamptz
        and valid <= '2018-02-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201801_idx on data_analog_201801(tower, valid);
  GRANT ALL on data_analog_201801 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201801 to tt_web;
  

  --
  CREATE TABLE data_sonic_201802(
  CONSTRAINT __data_sonic_201802_check
  CHECK(valid > '2018-02-01 00:00+00'::timestamptz
        and valid <= '2018-03-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201802_idx on data_sonic_201802(tower, valid);
  GRANT ALL on data_sonic_201802 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201802 to tt_web;

  --
  CREATE TABLE data_analog_201802(
  CONSTRAINT __data_analog_201802_check
  CHECK(valid > '2018-02-01 00:00+00'::timestamptz
        and valid <= '2018-03-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201802_idx on data_analog_201802(tower, valid);
  GRANT ALL on data_analog_201802 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201802 to tt_web;
  

  --
  CREATE TABLE data_sonic_201803(
  CONSTRAINT __data_sonic_201803_check
  CHECK(valid > '2018-03-01 00:00+00'::timestamptz
        and valid <= '2018-04-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201803_idx on data_sonic_201803(tower, valid);
  GRANT ALL on data_sonic_201803 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201803 to tt_web;

  --
  CREATE TABLE data_analog_201803(
  CONSTRAINT __data_analog_201803_check
  CHECK(valid > '2018-03-01 00:00+00'::timestamptz
        and valid <= '2018-04-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201803_idx on data_analog_201803(tower, valid);
  GRANT ALL on data_analog_201803 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201803 to tt_web;
  

  --
  CREATE TABLE data_sonic_201804(
  CONSTRAINT __data_sonic_201804_check
  CHECK(valid > '2018-04-01 00:00+00'::timestamptz
        and valid <= '2018-05-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201804_idx on data_sonic_201804(tower, valid);
  GRANT ALL on data_sonic_201804 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201804 to tt_web;

  --
  CREATE TABLE data_analog_201804(
  CONSTRAINT __data_analog_201804_check
  CHECK(valid > '2018-04-01 00:00+00'::timestamptz
        and valid <= '2018-05-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201804_idx on data_analog_201804(tower, valid);
  GRANT ALL on data_analog_201804 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201804 to tt_web;
  

  --
  CREATE TABLE data_sonic_201805(
  CONSTRAINT __data_sonic_201805_check
  CHECK(valid > '2018-05-01 00:00+00'::timestamptz
        and valid <= '2018-06-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201805_idx on data_sonic_201805(tower, valid);
  GRANT ALL on data_sonic_201805 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201805 to tt_web;

  --
  CREATE TABLE data_analog_201805(
  CONSTRAINT __data_analog_201805_check
  CHECK(valid > '2018-05-01 00:00+00'::timestamptz
        and valid <= '2018-06-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201805_idx on data_analog_201805(tower, valid);
  GRANT ALL on data_analog_201805 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201805 to tt_web;
  

  --
  CREATE TABLE data_sonic_201806(
  CONSTRAINT __data_sonic_201806_check
  CHECK(valid > '2018-06-01 00:00+00'::timestamptz
        and valid <= '2018-07-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201806_idx on data_sonic_201806(tower, valid);
  GRANT ALL on data_sonic_201806 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201806 to tt_web;

  --
  CREATE TABLE data_analog_201806(
  CONSTRAINT __data_analog_201806_check
  CHECK(valid > '2018-06-01 00:00+00'::timestamptz
        and valid <= '2018-07-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201806_idx on data_analog_201806(tower, valid);
  GRANT ALL on data_analog_201806 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201806 to tt_web;
  

  --
  CREATE TABLE data_sonic_201807(
  CONSTRAINT __data_sonic_201807_check
  CHECK(valid > '2018-07-01 00:00+00'::timestamptz
        and valid <= '2018-08-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201807_idx on data_sonic_201807(tower, valid);
  GRANT ALL on data_sonic_201807 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201807 to tt_web;

  --
  CREATE TABLE data_analog_201807(
  CONSTRAINT __data_analog_201807_check
  CHECK(valid > '2018-07-01 00:00+00'::timestamptz
        and valid <= '2018-08-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201807_idx on data_analog_201807(tower, valid);
  GRANT ALL on data_analog_201807 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201807 to tt_web;
  

  --
  CREATE TABLE data_sonic_201808(
  CONSTRAINT __data_sonic_201808_check
  CHECK(valid > '2018-08-01 00:00+00'::timestamptz
        and valid <= '2018-09-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201808_idx on data_sonic_201808(tower, valid);
  GRANT ALL on data_sonic_201808 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201808 to tt_web;

  --
  CREATE TABLE data_analog_201808(
  CONSTRAINT __data_analog_201808_check
  CHECK(valid > '2018-08-01 00:00+00'::timestamptz
        and valid <= '2018-09-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201808_idx on data_analog_201808(tower, valid);
  GRANT ALL on data_analog_201808 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201808 to tt_web;
  

  --
  CREATE TABLE data_sonic_201809(
  CONSTRAINT __data_sonic_201809_check
  CHECK(valid > '2018-09-01 00:00+00'::timestamptz
        and valid <= '2018-10-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201809_idx on data_sonic_201809(tower, valid);
  GRANT ALL on data_sonic_201809 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201809 to tt_web;

  --
  CREATE TABLE data_analog_201809(
  CONSTRAINT __data_analog_201809_check
  CHECK(valid > '2018-09-01 00:00+00'::timestamptz
        and valid <= '2018-10-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201809_idx on data_analog_201809(tower, valid);
  GRANT ALL on data_analog_201809 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201809 to tt_web;
  

  --
  CREATE TABLE data_sonic_201810(
  CONSTRAINT __data_sonic_201810_check
  CHECK(valid > '2018-10-01 00:00+00'::timestamptz
        and valid <= '2018-11-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201810_idx on data_sonic_201810(tower, valid);
  GRANT ALL on data_sonic_201810 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201810 to tt_web;

  --
  CREATE TABLE data_analog_201810(
  CONSTRAINT __data_analog_201810_check
  CHECK(valid > '2018-10-01 00:00+00'::timestamptz
        and valid <= '2018-11-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201810_idx on data_analog_201810(tower, valid);
  GRANT ALL on data_analog_201810 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201810 to tt_web;
  

  --
  CREATE TABLE data_sonic_201811(
  CONSTRAINT __data_sonic_201811_check
  CHECK(valid > '2018-11-01 00:00+00'::timestamptz
        and valid <= '2018-12-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201811_idx on data_sonic_201811(tower, valid);
  GRANT ALL on data_sonic_201811 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201811 to tt_web;

  --
  CREATE TABLE data_analog_201811(
  CONSTRAINT __data_analog_201811_check
  CHECK(valid > '2018-11-01 00:00+00'::timestamptz
        and valid <= '2018-12-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201811_idx on data_analog_201811(tower, valid);
  GRANT ALL on data_analog_201811 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201811 to tt_web;
  

  --
  CREATE TABLE data_sonic_201812(
  CONSTRAINT __data_sonic_201812_check
  CHECK(valid > '2018-12-01 00:00+00'::timestamptz
        and valid <= '2018-01-01 00:00+00'))
  INHERITS(data_sonic);
  CREATE INDEX data_sonic_201812_idx on data_sonic_201812(tower, valid);
  GRANT ALL on data_sonic_201812 to tt_script,tt_admin;
  GRANT SELECT on data_sonic_201812 to tt_web;

  --
  CREATE TABLE data_analog_201812(
  CONSTRAINT __data_analog_201812_check
  CHECK(valid > '2018-12-01 00:00+00'::timestamptz
        and valid <= '2019-01-01 00:00+00'))
  INHERITS(data_analog);
  CREATE INDEX data_analog_201812_idx on data_analog_201812(tower, valid);
  GRANT ALL on data_analog_201812 to tt_script,tt_admin;
  GRANT SELECT on data_analog_201812 to tt_web;
  
COMMIT;
