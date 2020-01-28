#!/usr/bin/env python
# Objctive: This program will do the following:
#     * retrieve the data from Cassandra
print "HELLO?????"
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

import json
import csv
import sys

data =[]
'''
# set the default program encoding to 'utf-8'
reload( sys )
sys.setdefaultencoding( 'utf-8' )
'''
from datetime import datetime
from datetime import timedelta
import time
start_time = time.time()


# ##################################################
# Cassandra Connection Configuration
# ----------------------------------------
# the server address
Cassandra_SERVER = '140.113.86.130'
# the user account and passwd for the participating party
Cassandra_USER = 'lassdb'
Cassandra_PASS = 'lassdb@dataarchive0222'
# the request consistency level setting
# doc: https://datastax.github.io/python-driver/api/cassandra.html#cassandra.ConsistencyLevel
Cassandra_CONSISTLEVEL = 1
# for large request, the result will be automatically paged
# set the size of each page
# doc: https://datastax.github.io/python-driver/api/cassandra/query.html#cassandra.query.Statement
Cassandra_FETCH_SIZE = 100
# set the timeout for the command execution in seconds
Cassandra_TIMEOUT = 60

# the name of the Cassandra Archive Table
Cassandra_ARCHIVE = 'archive'

# Source List Configuration
# ----------------------------------------

# this array contains all the data sources
#LIST_SOURCES = [ 'LASS', 'LASS4U', 'Indie', 'ProbeCube', 'WEBDUINO', 'AirBox', 'AsusAirBox', 'MAPS', 'EPA', 'CWB' ]
#LIST_SOURCES = ['EPA']
LIST_SOURCES = ['AirBox']

# ##################################################

print("--- %s seconds ---" % (time.time() - start_time))

# Database Connection ------------------------------
# connect to Cassandra
auth_provider = PlainTextAuthProvider( username = Cassandra_USER, password = Cassandra_PASS )
# bypass the ssl check hostname procedure, which enables the program to connect to cassandra through local IP
ssl_options = {'check_hostname': False}
casscluster = Cluster( [ Cassandra_SERVER ], auth_provider = auth_provider, ssl_options = ssl_options )
casssession = casscluster.connect( Cassandra_ARCHIVE )
casssession.default_timeout = 60
# ------------------------------ Database Connection

##################################################
# the following parameters should be modified:
YEAR = 2017
MONTH = 02
DAY = 06
##################################################

print("--- %s seconds ---" % (time.time() - start_time))


# start to archive the data
for SOURCE in LIST_SOURCES:
	# the Cassandra query command
	# ------------------------------
	# notes that:
	#  1. it is require to provide the source name!
	#  2. DO NOT REMOVE THE "ALLOW FILTERING" OPTION!
	# ------------------------------
	# query for 1 month's data:
	#Command = "SELECT data FROM " + Cassandra_ARCHIVE +  ".all WHERE source='" + SOURCE + "' and year=" + str( YEAR ) + " and month=" + str( int( MONTH ) ) + " ALLOW FILTERING;"
	# query for a date (ex. 2017-02-01):
	Command = "SELECT data FROM " + Cassandra_ARCHIVE +  ".all WHERE source='" + SOURCE + "' and year=" + str( YEAR ) + " and month=" + str( int( MONTH ) ) + " and day=" + str( int( DAY ) ) + " ALLOW FILTERING;"
	statement = SimpleStatement( Command, consistency_level = Cassandra_CONSISTLEVEL, fetch_size = Cassandra_FETCH_SIZE )

	try:
		# start archiving the data to the local database here!
		# ############################################################
		for result in casssession.execute( statement, timeout = Cassandra_TIMEOUT ):
			record = str(result.data).replace( '\n', '' ).replace( '\r', '' ).encode( 'utf-8' )
			#print(record)
			
			##### your code here... #####
			
			data.append(record)

		#print data


		with open("pm25_airbox_0206.txt", "w") as output:
			output.write(data)


		#json_data = json.dump(data)	
		#with open('pm25_airbox_0206.json', 'w') as output:
			#json.dump(json_data, output)

		#keys = data[0].keys()
		#with open('pm25_airbox_0206.csv', 'wb') as output_file:
			#dict_writer = csv.DictWriter(output_file, keys)
    		#dict_writer.writeheader()
    		#dict_writer.writerows(data)


  
		#f = csv.writer(open("pm25_epa_0206.csv","w"))
		#for x in data :
			#f.writerow([x["ver_format"],x["fmt_opt"],x["app"],x["ver_app"],x["device_id"],x["tick"],x["device"],x["s_0"],x["s_1"],x["s_2"],\
				#x["s_3"],x["s_d0"],x["s_d1"],x["s_d2"],x["s_t0"],x["s_h0"],x["gps_fix"],x["gps_num"],x["gps_alt"],x["date"],\
				#x["time"],x["SiteName"],x["loc"]["type"],x["loc"]["coordinates"]])

		#epa: 
		#for x in data :
			#f.writerow([x["ver_format"],x["fmt_opt"],x["app"],x["date"],x["time"],x["Status"],x["PSI"],x["CO"],x["SiteEngName"],x["PM10"],x["NO"],x["SiteName"],\
				#x["FPMI"],x["WindDirec"],x["PM2_5"],x["PublishTime"],x["County"],x["WindSpeed"],x["SO2"],x["NOx"],x["SiteType"],\
				#x["O3"],x["NO2"],x["loc"]["type"],x["loc"]["coordinates"]])


			 

		# ############################################################
	except Exception as ex:
		print( "[ERROR] (" + str( ex ) + ") Cassandra Query Error for the command: " + str( Command ) )
		print( "[ERROR] Probably no data available for this source!" )
		continue

# close the database connections
casscluster.shutdown()

print("--- %s seconds ---" % (time.time() - start_time))