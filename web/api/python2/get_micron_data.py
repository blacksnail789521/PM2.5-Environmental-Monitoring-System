import MySQLdb as mdb
import re
import os
import json


dbHost = '140.113.213.19'
dbUser = 'root'
dbPasswd = 'root0531'
db = 'micron'

query = 'SELECT * FROM %s WHERE monitor = \'%s\'  and d >= \'%s\' and d < \'%s\' and t >= \'%s\' and t < \'%s\''

def getData(table, param, startD, endD, startT, endT):
	global query
	conn = mdb.connect(dbHost, dbUser, dbPasswd, db)

	with conn:
		cursor = conn.cursor()
		cursor.execute(query % (table, param, startD, endD, startT, endT))
		data = cursor.fetchall()
		rowlist = []
		for row in data:
			rowlist.append({'rid': row[0], 'host': row[1], 'monitor': row[2], 'd': str(row[3]), 't': str(row[4]), 'value': float(row[5])})
		return json.dumps(rowlist)

if __name__ == '__main__':
	getData('host1', 'param30772', '2016-12-21', '2016-12-24', '23:35:26.000000', '23:59:24.000000')
