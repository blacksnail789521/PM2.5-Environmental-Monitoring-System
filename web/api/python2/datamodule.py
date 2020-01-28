from flask import Flask, request
from matrix_profile import matrix_profile
from get_real_time_data import get_real_time_data
from get_recent_data import get_recent_data
from get_micron_data import getData
import json


app = Flask(__name__)


@app.route('/hello', methods=['POST', 'GET'])
def hello_world():
        return request.args.get('name', '')

		
@app.route('/matrix_profile_web', methods=['POST', 'GET'])
def matrix_profile_web():
	#data = request.get_json()
	device_id = str(request.args.get('device_id', ''))
	start_date = str(request.args.get('start_date', ''))
	end_date = str(request.args.get('end_date', ''))
	sample_rate = int(request.args.get('sample_rate', ''))
	query_length = int(request.args.get('query_length', ''))
	time_mode = str(request.args.get('time_mode', ''))
	distance_function = str(request.args.get('distance_function', ''))
	number_of_motifs = int(request.args.get('number_of_motifs', ''))
	lower_limit_of_the_number_of_single_motif = int(request.args.get('lower_limit_of_the_number_of_single_motif', ''))
	#timestamp, pm25, tempature, humidity, mp, mpi, motif_index, discord_index = matrix_profile(device_id, start_date, end_date, sample_rate, query_length, time_mode, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif)
	#return json.dumps({'matrix_profile': mp, 'matrix_profile_index': mpi, 'motif_index': motif_index, 'discord_index': discord_index})
	#return json.dumps({'pm25' : pm25, 'matrix_profile': mp, 'matrix_profile_index': mpi, 'motif_index': motif_index, 'discord_index': discord_index})
	
	return matrix_profile(device_id, start_date, end_date, sample_rate, query_length, time_mode, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif)


@app.route('/micron/get_micron_data', methods=['POST'])
def get_M_data():
	table = str(request.args.get('table', ''))
	param = str(request.args.get('param', ''))
	startD = str(request.args.get('startD', ''))
	endD = str(request.args.get('endD', ''))
	startT = str(request.args.get('startT', ''))
	endT = str(request.args.get('endT', ''))
	return getData(table, param, startD, endD, startT, endT)

	
if __name__ == '__main__':
    app.debug = True
    app.run()
