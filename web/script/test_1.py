import json
import requests

device_id = "123"
current_date = "2017-07-22"

res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + current_date)
                
input_json_file = {}
if not res.json()['feeds']:
    # no data
    pass
else:
    if 'AirBox' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["AirBox"]
    elif 'LASS' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["LASS"]

with open("test.json", "w") as json_file:
    json.dump(input_json_file, json_file)