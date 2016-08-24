-- The storage of 20 Hz data in no-sql form was simply too large to work out
-- so we are going to do things the more hacky way
BEGIN;
CREATE TABLE towers(
  id smallint UNIQUE NOT NULL,
  name varchar);
INSERT into towers values(0, 'Hamilton');
INSERT into towers values(1, 'Story');

CREATE TABLE data_sonic(
  tower smallint REFERENCES towers(id),
  valid timestamptz,

  diag_5m smallint,
  ts_5m real,
  uz_5m real,
  uy_5m real,
  ux_5m real,

  diag_10m smallint,
  ts_10m real,
  uz_10m real,
  uy_10m real,
  ux_10m real,

  diag_20m smallint,
  ts_20m real,
  uz_20m real,
  uy_20m real,
  ux_20m real,
  
  diag_40m smallint,
  ts_40m real,
  uz_40m real,
  uy_40m real,
  ux_40m real,
  
  diag_80m smallint,
  ts_80m real,
  uz_80m real,
  uy_80m real,
  ux_80m real,
  
  diag_120m smallint,
  ts_120m real,
  uz_120m real,
  uy_120m real,
  ux_120m real);
GRANT ALL on data_sonic to tt_admin,tt_script;
GRANT SELECT on data_sonic to tt_web;

CREATE TABLE data_analog(
  tower smallint REFERENCES towers(id),
  valid timestamptz,

  ws_5m_s real,
  ws_5m_nw real,
  winddir_5m_s real,
  winddir_5m_nw real,
  rh_5m real,
  airtc_5m real,

  ws_10m_s real,
  ws_10m_nwht real,
  winddir_10m_s real,
  winddir_10m_nw real,
  rh_10m real,
  airtc_10m real,
  bp_10m real,

  ws_20m_s real,
  ws_20m_nw real,
  winddir_20m_s real,
  winddir_20m_nw real,
  rh_20m real,
  airtc_20m real,
  
  ws_40m_s real,
  ws_40m_nwht real,
  winddir_40m_s real,
  winddir_40m_nw real,
  rh_40m real,
  airtc_40m real,

  ws_80m_s real,
  ws_80m_nw real,
  winddir_80m_s real,
  winddir_80m_nw real,
  rh_80m real,
  airtc_80m real,
  bp_80m real,

  ws_120m_s real,
  ws_120m_nwht real,
  winddir_120m_s real,
  winddir_120m_nw real,
  rh_120m_1 real,
  rh_120m_2 real,
  airtc_120m_1 real,
  airtc_120m_2 real

);
GRANT ALL on data_analog to tt_admin,tt_script;
GRANT SELECT on data_analog to tt_web;

CREATE TABLE data_monitor(
  tower smallint REFERENCES towers(id),
  valid timestamptz,
  CR6_BattV real,
  CR6_PTemp real,
  BoardTemp_120m real,
  BoardHumidity_120m real,
  InclinePitch_120m real,
  InclineRoll_120m real,
  BoardTemp_80m real,
  BoardHumidity_80m real,
  InclinePitch_80m real,
  InclineRoll_80m real,
  BoardTemp_40m real,
  BoardHumidity_40m real,
  InclinePitch_40m real,
  InclineRoll_40m real,
  BoardTemp_20m real,
  BoardHumidity_20m real,
  InclinePitch_20m real,
  InclineRoll_20m real,
  BoardTemp_10m real,
  BoardHumidity_10m real,
  InclinePitch_10m real,
  InclineRoll_10m real,
  BoardTemp_5m real,
  BoardHumidity_5m real,
  InclinePitch_5m real,
  InclineRoll_5m real);
GRANT ALL on data_monitor to tt_admin,tt_script;
GRANT SELECT on data_monitor to tt_web;
COMMIT;
