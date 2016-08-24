
psql -c "create database talltowers;" -U postgres
psql -f createroles.sql -U postgres
psql -U tt_admin -f createtables.sql talltowers
psql -U tt_admin -f table-dat-partition.sql talltowers
psql -U tt_admin -f tablesv2.sql talltowers
python make_partitions.py | psql -U tt_admin talltowers
