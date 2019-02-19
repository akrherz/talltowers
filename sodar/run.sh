sleep 305
python process_sodar.py $(date -u --date '5 minutes ago' +'%Y %m %d %H %M')
