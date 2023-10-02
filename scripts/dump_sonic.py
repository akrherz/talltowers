import psycopg2

pgconn = psycopg2.connect(
    database="talltowers",
    host="talltowers-db.agron.iastate.edu",
    user="tt_web",
)
cursor = pgconn.cursor()

tower = 1
cursor.execute(
    """
    SELECT tower,
        valid at time zone 'America/Chicago' as localvalid,
    *
    from data_sonic WHERE tower = %s and
    valid between '2016-07-06 05:00+00' and '2016-07-07 05:00+00'
    ORDER by localvalid"""
    % (tower,)
)
o = open("story_sonic.csv", "w")
for row in cursor:
    o.write(",".join([str(s) for s in row]) + "\n")

o.close()
