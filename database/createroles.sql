-- create roles for talltowers database
-- NOTE:  postgres must have a login (pg_hba) and database must already exist, do these by:
---------
-- sudo -i
-- su postgres
-- psql
-- \password
-- \q
-- exit  --> back to root
-- vi /etc/postgresql/9.5/main/pg_hba.conf  --> add "local	all	all	md5"; comment out line with "local all postgres	peer"
-- servicectl restart postgres-9.5
-- exit  --> back to initial user
---------
--createdb -h localhost -U postgres --owner postgres talltowers
-- call this file with:
--psql -h localhost -U postgres -d talltowers --file /dirpath/createroles.sql

-- roles
CREATE ROLE tt_admin SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN password 'changeme';
CREATE ROLE tt_script NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN password 'changeme';
CREATE ROLE tt_web NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN password 'changeme';

-- alter passwords with one of the following:
--via SQL
--ALTER USER tt_admin WITH ENCRYPTED PASSWORD 'encyptedpassword';
--via psql
--\password tt_admin

COMMENT ON ROLE tt_admin IS 'superuser for talltowers.  This should be used instead of "postgres" for adminstrative tasks.';
COMMENT ON ROLE tt_script IS 'the login for the python script; has INSERT (& COPY) privlidges on dat table.';
COMMENT ON ROLE tt_web IS 'read only user.  used by PHP server side scripts to extract data from database.';

-- grant access to non-superusers
-- first clear out public permissions
REVOKE CONNECT ON DATABASE talltowers FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
-- tt_web
GRANT CONNECT ON DATABASE talltowers TO tt_web;
GRANT USAGE ON SCHEMA public TO tt_web;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO tt_web;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO tt_web;
GRANT TEMPORARY ON DATABASE talltowers TO tt_web;
-- tt_script
GRANT CONNECT ON DATABASE talltowers TO tt_script;
GRANT USAGE ON SCHEMA public TO tt_script;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO tt_script;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO tt_script;
GRANT TEMPORARY ON DATABASE talltowers TO tt_script;

-- NOTE:  table dat not made yet, but when it is, the following is run it the createtables.sql code:
--GRANT INSERT ON TABLE dat TO tt_script;


-- NOTE:  no sequences, so no need for
--GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO tt_web;
-- need to verify...

-- next create tables.  call that file with:
--psql -h localhost -U postgres -d talltowers --file createtables.sql

