-- create tables for talltowers
-- call this file with:
--psql -h localhost -U tt_admin -d talltowers --file dirpath/createtables.sql
-- NOTEs:
--  * must already have database, assumes that the previos commands have been run from command line of database server:
-- 	* tt_admin has psssword (\password tt_admin), as well as other roles
--	* the user is "tt_admin", who will own the tables, eventhough postgres owns the database.
--createdb -h localhost -U postgres --owner postgres talltowers
--psql -h localhost -U postgres -d talltowers --file createroles.sql
--...and passwords for tt_admin, tt_script, & tt_web have been created


CREATE TABLE channels (
  chn_id smallint NOT NULL,
  header varchar(20) NOT NULL,
  height smallint,
  site varchar(8) NOT NULL,
  unit varchar(4)
);

COMMENT ON TABLE channels IS 'This table provides the chn_id to select from the dat table.';
COMMENT ON COLUMN channels.chn_id IS 'primary key. encoded with site as thousands unit, datatable as hundreds, and tens+ones are the column number in .dat files.';
COMMENT ON COLUMN channels.header IS 'the column name programmed by the datalogger.  when important, the header includes height in meters.';
COMMENT ON COLUMN channels.height IS 'the height in meters above ground.  The datashed does not have a height ("\N")';
COMMENT ON COLUMN channels.site IS '"story" or "hamilton"';
COMMENT ON COLUMN channels.unit IS 'units of measurment';

ALTER TABLE ONLY channels ADD CONSTRAINT channels_pkey PRIMARY KEY (chn_id);


CREATE TABLE dat (
    ts timestamptz NOT NULL,
    chn_id smallint NOT NULL,
    val real
);

COMMENT ON TABLE dat IS 'Raw data table in 6th normal form. This is a Parent table; child tables are partitioned by month, and they where data is actually stored.';
COMMENT ON COLUMN dat.ts IS 'first field in componsit key.  Timestamptz is 8-byte postgres datatype;  This includes timezone.';
COMMENT ON COLUMN dat.chn_id IS 'second field in composit key.  Unique channel identifier, foreign key to "channels" table.';
COMMENT ON COLUMN dat.val IS 'the actual data sotred as 4-Byte floats.';

--ALTER TABLE ONLY dat ADD CONSTRAINT dat_pkey PRIMARY KEY (channel_id, ts_id);
-- ...not included here, because data should be added, before indexing.
-- ...Also, primary keys/indexes are applied to the daughter tables, not the parent table, which is essentially empty!!!
--ALTER TABLE ONLY dat ADD CONSTRAINT dat_channel_fkey FOREIGN KEY (chn_id) REFERENCES channels(chn_id);


-- grant insert to "tt_script"
GRANT INSERT ON TABLE dat TO tt_script;


-- copy channels data
-- developed from headers, using python code "simple_chn_id.py".
COPY channels (chn_id,header,height,site,unit) FROM stdin;
1102	AirTC_120m_1	120	story	C
1103	AirTC_120m_2	120	story	C
1104	AirTC_80m	80	story	C
1105	AirTC_40m	40	story	C
1106	AirTC_20m	20	story	C
1107	AirTC_10m	10	story	C
1108	AirTC_5m	5	story	C
1109	RH_120m_1	120	story	%
1110	RH_120m_2	120	story	%
1111	RH_80m	80	story	%
1112	RH_40m	40	story	%
1113	RH_20m	20	story	%
1114	RH_10m	10	story	%
1115	RH_5m	5	story	%
1116	BP_80m	80	story	mbar
1117	BP_10m	10	story	mbar
1118	WS_120m_NWht	120	story	m/s
1119	WS_120m_S	120	story	m/s
1120	WS_80m_NW	80	story	m/s
1121	WS_80m_S	80	story	m/s
1122	WS_40m_NWht	40	story	m/s
1123	WS_40m_S	40	story	m/s
1124	WS_20m_NW	20	story	m/s
1125	WS_20m_S	20	story	m/s
1126	WS_10m_NWht	10	story	m/s
1127	WS_10m_S	10	story	m/s
1128	WS_5m_NW	5	story	m/s
1129	WS_5m_S	5	story	m/s
1130	WindDir_120m_NW	120	story	deg
1131	WindDir_120m_S	120	story	deg
1132	WindDir_80m_NW	80	story	deg
1133	WindDir_80m_S	80	story	deg
1134	WindDir_40m_NW	40	story	deg
1135	WindDir_40m_S	40	story	deg
1136	WindDir_20m_NW	20	story	deg
1137	WindDir_20m_S	20	story	deg
1138	WindDir_10m_NW	10	story	deg
1139	WindDir_10m_S	10	story	deg
1140	WindDir_5m_NW	5	story	deg
1141	WindDir_5m_S	5	story	deg
1202	Ux_120m	120	story	m/s
1203	Uy_120m	120	story	m/s
1204	Uz_120m	120	story	m/s
1205	Ts_120m	120	story	C
1206	Diag_120m	120	story	
1207	Ux_80m	80	story	m/s
1208	Uy_80m	80	story	m/s
1209	Uz_80m	80	story	m/s
1210	Ts_80m	80	story	C
1211	Diag_80m	80	story	
1212	Ux_40m	40	story	m/s
1213	Uy_40m	40	story	m/s
1214	Uz_40m	40	story	m/s
1215	Ts_40m	40	story	C
1216	Diag_40m	40	story	
1217	Ux_20m	20	story	m/s
1218	Uy_20m	20	story	m/s
1219	Uz_20m	20	story	m/s
1220	Ts_20m	20	story	C
1221	Diag_20m	20	story	
1222	Ux_10m	10	story	m/s
1223	Uy_10m	10	story	m/s
1224	Uz_10m	10	story	m/s
1225	Ts_10m	10	story	C
1226	Diag_10m	10	story	
1227	Ux_5m	5	story	m/s
1228	Uy_5m	5	story	m/s
1229	Uz_5m	5	story	m/s
1230	Ts_5m	5	story	C
1231	Diag_5m	5	story	
1302	CR6_BattV	\N	story	V
1303	CR6_PTemp	\N	story	C
1304	BoardTemp_120m	120	story	C
1305	BoardHumidity_120m	120	story	%
1306	InclinePitch_120m	120	story	deg
1307	InclineRoll_120m	120	story	deg
1308	BoardTemp_80m	80	story	C
1309	BoardHumidity_80m	80	story	%
1310	InclinePitch_80m	80	story	deg
1311	InclineRoll_80m	80	story	deg
1312	BoardTemp_40m	40	story	C
1313	BoardHumidity_40m	40	story	%
1314	InclinePitch_40m	40	story	deg
1315	InclineRoll_40m	40	story	deg
1316	BoardTemp_20m	20	story	C
1317	BoardHumidity_20m	20	story	%
1318	InclinePitch_20m	20	story	deg
1319	InclineRoll_20m	20	story	deg
1320	BoardTemp_10m	10	story	C
1321	BoardHumidity_10m	10	story	%
1322	InclinePitch_10m	10	story	deg
1323	InclineRoll_10m	10	story	deg
1324	BoardTemp_5m	5	story	C
1325	BoardHumidity_5m	5	story	%
1326	InclinePitch_5m	5	story	deg
1327	InclineRoll_5m	5	story	deg
2102	AirTC_120m_1	120	hamilton	C
2103	AirTC_120m_2	120	hamilton	C
2104	AirTC_80m	80	hamilton	C
2105	AirTC_40m	40	hamilton	C
2106	AirTC_20m	20	hamilton	C
2107	AirTC_10m	10	hamilton	C
2108	AirTC_5m	5	hamilton	C
2109	RH_120m_1	120	hamilton	%
2110	RH_120m_2	120	hamilton	%
2111	RH_80m	80	hamilton	%
2112	RH_40m	40	hamilton	%
2113	RH_20m	20	hamilton	%
2114	RH_10m	10	hamilton	%
2115	RH_5m	5	hamilton	%
2116	BP_80m	80	hamilton	mbar
2117	BP_10m	10	hamilton	mbar
2118	WS_120m_NWht	120	hamilton	m/s
2119	WS_120m_S	120	hamilton	m/s
2120	WS_80m_NW	80	hamilton	m/s
2121	WS_80m_S	80	hamilton	m/s
2122	WS_40m_NWht	40	hamilton	m/s
2123	WS_40m_S	40	hamilton	m/s
2124	WS_20m_NW	20	hamilton	m/s
2125	WS_20m_S	20	hamilton	m/s
2126	WS_10m_NWht	10	hamilton	m/s
2127	WS_10m_S	10	hamilton	m/s
2128	WS_5m_NW	5	hamilton	m/s
2129	WS_5m_S	5	hamilton	m/s
2130	WindDir_120m_NW	120	hamilton	deg
2131	WindDir_120m_S	120	hamilton	deg
2132	WindDir_80m_NW	80	hamilton	deg
2133	WindDir_80m_S	80	hamilton	deg
2134	WindDir_40m_NW	40	hamilton	deg
2135	WindDir_40m_S	40	hamilton	deg
2136	WindDir_20m_NW	20	hamilton	deg
2137	WindDir_20m_S	20	hamilton	deg
2138	WindDir_10m_NW	10	hamilton	deg
2139	WindDir_10m_S	10	hamilton	deg
2140	WindDir_5m_NW	5	hamilton	deg
2141	WindDir_5m_S	5	hamilton	deg
2202	Ux_120m	120	hamilton	m/s
2203	Uy_120m	120	hamilton	m/s
2204	Uz_120m	120	hamilton	m/s
2205	Ts_120m	120	hamilton	C
2206	Diag_120m	120	hamilton	
2207	Ux_80m	80	hamilton	m/s
2208	Uy_80m	80	hamilton	m/s
2209	Uz_80m	80	hamilton	m/s
2210	Ts_80m	80	hamilton	C
2211	Diag_80m	80	hamilton	
2212	Ux_40m	40	hamilton	m/s
2213	Uy_40m	40	hamilton	m/s
2214	Uz_40m	40	hamilton	m/s
2215	Ts_40m	40	hamilton	C
2216	Diag_40m	40	hamilton	
2217	Ux_20m	20	hamilton	m/s
2218	Uy_20m	20	hamilton	m/s
2219	Uz_20m	20	hamilton	m/s
2220	Ts_20m	20	hamilton	C
2221	Diag_20m	20	hamilton	
2222	Ux_10m	10	hamilton	m/s
2223	Uy_10m	10	hamilton	m/s
2224	Uz_10m	10	hamilton	m/s
2225	Ts_10m	10	hamilton	C
2226	Diag_10m	10	hamilton	
2227	Ux_5m	5	hamilton	m/s
2228	Uy_5m	5	hamilton	m/s
2229	Uz_5m	5	hamilton	m/s
2230	Ts_5m	5	hamilton	C
2231	Diag_5m	5	hamilton	
2302	CR6_BattV	\N	hamilton	V
2303	CR6_PTemp	\N	hamilton	C
2304	BoardTemp_120m	120	hamilton	C
2305	BoardHumidity_120m	120	hamilton	%
2306	InclinePitch_120m	120	hamilton	deg
2307	InclineRoll_120m	120	hamilton	deg
2308	BoardTemp_80m	80	hamilton	C
2309	BoardHumidity_80m	80	hamilton	%
2310	InclinePitch_80m	80	hamilton	deg
2311	InclineRoll_80m	80	hamilton	deg
2312	BoardTemp_40m	40	hamilton	C
2313	BoardHumidity_40m	40	hamilton	%
2314	InclinePitch_40m	40	hamilton	deg
2315	InclineRoll_40m	40	hamilton	deg
2316	BoardTemp_20m	20	hamilton	C
2317	BoardHumidity_20m	20	hamilton	%
2318	InclinePitch_20m	20	hamilton	deg
2319	InclineRoll_20m	20	hamilton	deg
2320	BoardTemp_10m	10	hamilton	C
2321	BoardHumidity_10m	10	hamilton	%
2322	InclinePitch_10m	10	hamilton	deg
2323	InclineRoll_10m	10	hamilton	deg
2324	BoardTemp_5m	5	hamilton	C
2325	BoardHumidity_5m	5	hamilton	%
2326	InclinePitch_5m	5	hamilton	deg
2327	InclineRoll_5m	5	hamilton	deg
\.
