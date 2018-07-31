-- Storage of SODAR data
CREATE TABLE sodar_profile(
    station int,
    valid timestamptz,
    label char(1),
    height int,
    beamnum real,
    confidence_function real,
    confidence real,
    echo_suppression real,
    number_of_shots real,
    peak_detection real,
    range_gate real,
    signal_level real,
    snr real,
    suppressed_echoes real,
    valid_spectra real,
    wind_direction real,
    wind_speed real,
    wind_vert real,
    quality real,
    wind_turbulence real
);
CREATE UNIQUE INDEX soldar_profile_idx on
  sodar_profile(station, valid, label, height);
GRANT ALL on sodar_profile to tt_script;
GRANT SELECT on sodar_surface to tt_web;

CREATE TABLE sodar_surface(
    station int,
    valid timestamptz,
    ambient_temp real,
    barometric_pressure real,
    tiltx real,
    azimuth real,
    tilty real,
    humidity real,
    noise_level_a real,
    noise_level_b real,
    noise_level_c real,
    solar_power real,
    cpu_power real,
    core_power real,
    modem_power real,
    speaker_power real,
    pwm_power real,
    status real,
    internal_temp real,
    heater_temp real,
    mirror_temp real,
    cpu_temp real,
    vibrationy real,
    vibrationx real,
    battery real,
    beep_volume real
);
CREATE UNIQUE INDEX sodar_surface_idx on sodar_surface(station, valid);
GRANT ALL on sodar_surface to tt_script;
GRANT SELECT on sodar_surface to tt_web;
