import datetime
import psycopg2
from ansible.modules.extras.cloud.amazon import sts_assume_role

pgconn = psycopg2.connect(database='talltowers',
                          host='talltowers-db.agron.iastate.edu',
                          user='tt_web')
cursor = pgconn.cursor()

schema = """ tower           | smallint                 | 
 valid           | timestamp with time zone | 
 ws_5m_s         | real                     | 
 ws_5m_nw        | real                     | 
 winddir_5m_s    | real                     | 
 winddir_5m_nw   | real                     | 
 rh_5m           | real                     | 
 airtc_5m        | real                     | 
 ws_10m_s        | real                     | 
 ws_10m_nwht     | real                     | 
 winddir_10m_s   | real                     | 
 winddir_10m_nw  | real                     | 
 rh_10m          | real                     | 
 airtc_10m       | real                     | 
 bp_10m          | real                     | 
 ws_20m_s        | real                     | 
 ws_20m_nw       | real                     | 
 winddir_20m_s   | real                     | 
 winddir_20m_nw  | real                     | 
 rh_20m          | real                     | 
 airtc_20m       | real                     | 
 ws_40m_s        | real                     | 
 ws_40m_nwht     | real                     | 
 winddir_40m_s   | real                     | 
 winddir_40m_nw  | real                     | 
 rh_40m          | real                     | 
 airtc_40m       | real                     | 
 ws_80m_s        | real                     | 
 ws_80m_nw       | real                     | 
 winddir_80m_s   | real                     | 
 winddir_80m_nw  | real                     | 
 rh_80m          | real                     | 
 airtc_80m       | real                     | 
 bp_80m          | real                     | 
 ws_120m_s       | real                     | 
 ws_120m_nwht    | real                     | 
 winddir_120m_s  | real                     | 
 winddir_120m_nw | real                     | 
 rh_120m_1       | real                     | 
 rh_120m_2       | real                     | 
 airtc_120m_1    | real                     | 
 airtc_120m_2    | real                     | """
cols = []
for line in schema.split("\n"):
    cols.append(line.strip().split()[0])

sql = []
for col in cols[2:]:
    sql.append(" avg(%s) as avg_%s" % (col, col))
sql = ",".join(sql)

for tower in range(2):
    sts = datetime.date(2016, 3, 31)
    ets = datetime.date(2016, 9, 14)
    interval = datetime.timedelta(days=1)
    now = sts
    o = open("analog%s.txt" % (tower,), 'wb')
    o.write(",".join(cols) + "\n")
    while now < ets:
        print now
        cursor.execute("""
            SELECT tower,
            date_trunc('minute',
                valid at time zone 'America/Chicago') as localvalid,
            """ + sql + """
            from data_analog WHERE tower = %s and
            valid between '%s 06:00+00' and '%s 06:00+00'
            GROUP by tower, localvalid
            ORDER by localvalid""" % (tower, now.strftime("%Y-%m-%d"),
                                      (now + interval).strftime("%Y-%m-%d")
                                      ))
        for row in cursor:
            o.write(",".join([str(s) for s in row]) + "\n")
        now += interval
    o.close()
