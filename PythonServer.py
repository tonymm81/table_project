import logging
from flask import Flask, request, jsonify
import ssl
from flask_cors import CORS
import wlan_devices as wlandevices
import json 


# Luo Flask-sovellus
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Define the log file
logging.basicConfig(filename="/home/table/Desktop/table2/table_project/flaskserver_log.log",
                    level=logging.INFO, format="%(asctime)s - %(message)s")

#GET request
@app.route('/data', methods=['GET'])
def get_data():
    json_data = wlandevices.load_json()
    #json_data = json.loads(json_data_raw)
    #logging.info(f"GET-pyyntö vastaanotettu: {json_data}")
    #print(f"GET vastaanotettu: {json_data}")
    return jsonify(json_data)

#  post request
@app.route('/receive', methods=['POST'])
def receive_data():
    request_data = request.get_json()
    logging.info(f"POST-pyyntö vastaanotettu: {request_data}")
    print(f"POST vastaanotettu: {request_data}")
    if request_data is None:
        return jsonify({"error": "Virhe JSON-datan käsittelyssä!"}), 400
    #response_data = {"received": request_data, "status": "Success"}
    compare = wlandevices.load_json() 
    ComapreDevices(request_data, compare)
    return jsonify({"status": "Success", "received_data": request_data})


def ComapreDevices(json_data, compare, path=""): # here we compare if this device json object is different and if it
                                                   # then we change the devices status and restore the updated json object to program and phone
    print(f"🔍 json_data type: {type(json_data)} | data: {json_data}")
    if isinstance(json_data, dict) and isinstance(compare, dict):
        for key in json_data.keys() | compare.keys(): 
            new_path = f"{path}.{key}" if path else key
            if key not in json_data:
                print(f"Puuttuu JSON1: {new_path}")
            elif key not in compare:
                print(f" Puuttuu JSON2: {new_path}")
            else:
                ComapreDevices(json_data[key], compare[key], new_path)
    elif isinstance(json_data, list) and isinstance(compare, list):
        for i, (val1, val2) in enumerate(zip(json_data, compare)):
            ComapreDevices(val1, val2, f"{path}[{i}]")
    else:
        if json_data != compare:
            print(f" Ero arvoissa: {path} -> {json_data} vs {compare}")
            #here build up the code, what changes the devices state


# 🔧 **Palvelimen käynnistys**
if __name__ == '__main__':
    context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logging.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000)