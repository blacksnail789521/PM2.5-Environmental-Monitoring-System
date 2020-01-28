from flask import Flask, request
import json
from get_clean_data import get_clean_data_web
from get_recent_data import get_recent_data_web
from get_real_time_data import get_real_time_data_web
from compute_average_max_min import compute_average_max_min_web
from compute_matrix_profile import compute_matrix_profile_web


app = Flask(__name__)


@app.route('/hello', methods=['POST', 'GET'])
def hello_world():
    return request.args.get('name')


@app.route('/get_clean_data', methods=['POST', 'GET'])
def get_clean_data():
    device_id = str(request.args.get('device_id'))
    start_date = str(request.args.get('start_date'))
    end_date = str(request.args.get('end_date'))
    sample_rate = int(request.args.get('sample_rate'))
    days = request.args.getlist('days', type = int)
    hours = request.args.getlist('hours', type = int)
    
    return get_clean_data_web(device_id, start_date, end_date, sample_rate, days, hours)


@app.route('/get_recent_data', methods=['POST', 'GET'])
def get_recent_data():
    device_id = str(request.args.get('device_id'))
    
    return get_recent_data_web(device_id)


@app.route('/get_real_time_data', methods=['POST', 'GET'])
def get_real_time_data():
    return get_real_time_data_web()


@app.route('/compute_average_max_min', methods=['POST', 'GET'])
def compute_average_max_min():
    device_id = str(request.args.get('device_id'))
    start_date = str(request.args.get('start_date'))
    end_date = str(request.args.get('end_date'))
    sample_rate = int(request.args.get('sample_rate'))
    time_mode = str(request.args.get('time_mode'))
    
    return compute_average_max_min_web(device_id, start_date, end_date, sample_rate, time_mode)


@app.route('/compute_matrix_profile', methods=['POST', 'GET'])
def compute_matrix_profile():
	#data = request.get_json()
    device_id = str(request.args.get('device_id', ''))
    start_date = str(request.args.get('start_date', ''))
    end_date = str(request.args.get('end_date', ''))
    sample_rate = int(request.args.get('sample_rate', ''))
    days = request.args.getlist('days', type = int)
    hours = request.args.getlist('hours', type = int)
    query_length = int(request.args.get('query_length', ''))
    distance_function = str(request.args.get('distance_function', ''))
    number_of_motifs = int(request.args.get('number_of_motifs', ''))
    lower_limit_of_the_number_of_single_motif = int(request.args.get('lower_limit_of_the_number_of_single_motif', ''))
    
    return compute_matrix_profile_web(device_id, start_date, end_date, sample_rate, days, hours, query_length, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif)


if __name__ == '__main__':
    app.debug = True
    app.run()
