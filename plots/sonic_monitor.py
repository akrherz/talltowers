#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
make plot of recent data from talltowers project, for display on website.

# database definition:  
#  ALTER TABLE Dat ALTER COLUMN ts TYPE TIMESTAMP WITH TIME ZONE USING ts AT TIME ZONE 'UTC'
# note: the dataloggers are set to UTC, so their dates are put into the database as UTC.

written for pyton 3

@author: joe
"""

import datetime
from dateutil import tz
import psycopg2
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot.  
#   By default, matplotlib will use something like the TkAgg backend. 
#   This requires an X-server to be running.
#   To make a plot without needing an X-server at all, use the Agg backend instead.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# get database credentials
import os
import sys
if os.path.exists("/home/joesmith"):    # FTP server
    sys.path.append("/home/joesmith")
elif os.path.exists("/home/joe"):   # old home server
    sys.path.append("/home/joe")
elif os.path.exists(r"C:\Users\joe\TallTowers"):
    sys.path.append(r"C:\Users\joe\TallTowers")    # home workstation
else:
    sys.path.append(r"C:\Users\joesmith")   # ISU work computer
import pyenv


# === INPUTS ===

site_list = ['story','hamilton']
hours_back = 336
hour_interval = 24  # period of "%H:%M" tickmarks in hours
plot_dir = pyenv.dir_plot_www

# === plot dictionary ===
plot_dict = {'Sonic R.H.':   {'ffn_plot':"{}-sonic-RH.png", 'Y-label':'Relative Humidity [%]', 
                              'channels':['BoardHumidity_5m','BoardHumidity_10m','BoardHumidity_20m','BoardHumidity_40m','BoardHumidity_80m','BoardHumidity_120m']},
             'Sonic Brd-Tmp':{'ffn_plot':"{}-sonic-board-temp.png", 'Y-label':'Temperature [C]', 
                              'channels':['BoardTemp_5m','BoardTemp_10m','BoardTemp_20m','BoardTemp_40m','BoardTemp_80m','BoardTemp_120m']},
             'Sonic Pitch':  {'ffn_plot':"{}-sonic-pitch.png", 'Y-label':'Sonic Anemometer Pitch [deg]', 
                              'channels':['InclinePitch_5m','InclinePitch_10m','InclinePitch_20m','InclinePitch_40m','InclinePitch_80m','InclinePitch_120m']},
             'Sonic Roll':   {'ffn_plot':"{}-sonic-roll.png", 'Y-label':'Sonic Anemometer Role [deg]', 
                              'channels':['InclineRoll_5m','InclineRoll_10m','InclineRoll_20m','InclineRoll_40m','InclineRoll_80m','InclineRoll_120m']}
            }

for key, value in plot_dict.items():
    #print "{}\n  {}".format(key,value)  # <-------------- debug ---
    for site in site_list:
        #print "site: {}".format(site.upper())  # <-------------- debug ---
        # =================== GET TIME &  TIME STRING ====================
        time_now = datetime.datetime.utcnow().replace(tzinfo=tz.gettz('UTC'))
        time_data_start = time_now - datetime.timedelta(hours=hours_back)
        # timestamps for plotting
        ts_query_utc = datetime.datetime.strftime(time_now, "%d-%b-%y %H:%M UTC")
        ts_now_local = datetime.datetime.strftime(time_now.astimezone(tz.gettz('US/Central')), "%d-%b-%y %H:%M %Z")
        # =================== GET DATA FROM DATABASE =====================
        # creaee empty list to hold data from each channel
        dfs = []
        try:
            with psycopg2.connect('host={hostname} dbname={dbname} user={dbuser} password={dbpass}'.format(**pyenv.dbconn)) as conn:
                with conn.cursor() as cur:
                    for chn in value['channels']:
                        # get chn_id
                        cur.execute("""SELECT chn_id 
                                       FROM Channels 
                                       WHERE site = %s 
                                       AND header = %s;""",(site,chn) )
                        chn_id = cur.fetchall()[0][0]
                        # get data
                        #   note: datetime.datetime objects with a tz, will be
                        #       converted to postgres's "TIMESTAMPTZ" format
                        cur.execute("""SELECT date_trunc('minute', ts), AVG(val)
                                    FROM Dat
                                    WHERE chn_id = %s
                                    AND ts > %s
                                    AND ts < %s
                                    GROUP BY date_trunc('minute', ts)
                                    ORDER BY date_trunc('minute', ts);""",(chn_id,time_data_start,time_now) )
                        data = cur.fetchall()
                        # make pandas.DataFrame object
                        df_raw = pd.DataFrame(data, columns=['ts',chn]).set_index('ts')
                        df_raw.columns = [ "_".join([site.capitalize(), df_raw.columns[0]]) ]
                        dfs.append( df_raw )
        except Exception as e:
            #raise Exception('Failed to get data from database.\n',e)  # <-------------- debug ---
            break
        # ===================== PLOT DATA, IF ANY =======================
        # verify that data was returned
        if any([len(df_) > 0 for df_ in dfs]):
            # combine all channels into one data frame
            df = pd.concat(dfs, axis=1)
            # verify that dat is not all NANs
            if len(df.dropna(how='all')) > 0:
                # === PLOT ===
                fig,ax = plt.subplots(figsize=(17,11))
                # do not rely on Pandas.DataFrame.plot(), because it uses differnet dates than
                #   matplotlib, and because matplot lib will be invoked to customize this plo, 
                #   keep it matplotlib thoughout.
                ts = df.index
                for col in df:
                    ax.plot(ts, df[col], label=col)
                # set legend and titles
                lgnd = ax.legend(loc='best')
                plot_title = "One minute average of last {} hours of {} from {}".format(hours_back,key,site.upper())
                ax.set_title(plot_title, fontsize=22)
                # set texts with times
                fig.text(x=0.98,y=0.99, s='   generated at   \n' + ts_now_local, 
                             color='#888888', ha='right', va='top', fontsize=12)
                ts_db_last = df.index[-1].astimezone(tz.gettz('UTC')).strftime('%d-%b-%y %H:%M UTC')
                fig.text(x=0.98,y=0.01, s='newest data:' + ts_db_last + '\nquery at: ' + ts_query_utc, 
                             color='#888888', ha='right', va='bottom', fontsize=10)
                # set all tick parameters, e.g.
                ax.tick_params(axis='both', which='both', labelsize=16)
                # format Y-axis
                ax.yaxis.set_label_text(value['Y-label'])
                ax.yaxis.label.set_size(16)
                ax.yaxis.grid(True)
                # format X-axis labels
                ax.xaxis.set_label_text('Time [UTC]')
                ax.xaxis.label.set_size(16)
                # format MINOR X-axis ticks & labels
                lacator_working = ax.xaxis.get_minor_locator()
                ax.xaxis.set_minor_locator(mdates.HourLocator(interval=hour_interval))
                ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.grid(True, which="minor")
                # format MINOR X-axis ticks & labels
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%d-%b\n%Y'))
                plt.setp(ax.get_xticklabels(), rotation=0, horizontalalignment='center')
                # clean & save
                fig.tight_layout()
            else:
                fig,ax = plt.subplots()
                textstr = "All Data returned\n      is NaN.\nNothing to plot!"
                ax.text(0.2, 0.35, textstr, transform=ax.transAxes, fontsize=34)
        else:
            fig,ax = plt.subplots()
            textstr = "No Data returned\n   from query!"
            ax.text(0.2, 0.40, textstr, transform=ax.transAxes, fontsize=34)
        
        # save figure
        ffn_plot = os.path.join(plot_dir,value['ffn_plot'].format(site))
        fig.savefig(ffn_plot,format='png')



'''
try:
conn = psycopg2.connect("host='10.27.19.214' dbname='talltowers' user='tt_web' password='...'")
conn = psycopg2.connect("host='192.168.0.2' dbname='talltowers' user='tt_web' password='...'")
conn = psycopg2.connect('host={hostname} dbname={dbname} user={dbuser} password={dbpass}'.format(**pyenv.dbconn))

cur = conn.cursor() #Create the cursor
for chn in channels:
    
chn = channels[0]

cur.mogrify("select chn_id from channels where site = %s and header = %s;",(site,chn) )
cur.execute("select chn_id from channels where site = %s and header = %s;",(site,chn) )
chn_id = cur.fetchall()[0][0]
#cur.execute("select ts,val from dat where chn_id = %s and ts > %s::timestamptz and ts < %s::timestamptz;",
#            (chn_id,ts_data_start,ts_data_end) )
##cur.execute / cur.mogrify
cur.mogrify("""SELECT date_trunc('minute', ts), AVG(val) 
            FROM dat 
            WHERE chn_id = %s 
            AND ts > %s::TIMESTAMPTZ 
            AND ts < %s::TIMESTAMPTZ 
            GROUP BY date_trunc('minute', ts) 
            ORDER BY date_trunc('minute', ts);""",(chn_id,ts_data_start,ts_data_end) )
data = cur.fetchall()
dfs.append( pd.DataFrame(data, columns=['ts',chn]).set_index('ts') )


conn.close()
'''