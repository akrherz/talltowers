
psql -c "create database talltowers;" -U postgress
psql -f createroles.sql -U postgres
psql -U tt_admin -f createtables.sql talltowers
psql -U tt_admin -f table-dat-partititon.sql talltowers
