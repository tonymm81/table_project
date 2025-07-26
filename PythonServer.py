import logging
from flask import Flask, request, jsonify
import ssl
from flask_cors import CORS
import wlan_devices as wlandevices
import json 
import os
import broadlink
import re
from motorcontrol import measure_table as MC
from pprint import pformat
# Luo Flask-sovellus
app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, supports_credentials=True)

# Define the log file
logger = logging.getLogger("pythonserver")
file_handler = logging.FileHandler("/home/table/Desktop/table2/table_project/flaskserver_log.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


BeforeCompare = {}
ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip() # this how we take broker ip address in beging of program-
devicesInServer = broadlink.discover(timeout=5, local_ip_address=ipv4)# lets check devices list '192.168.68.118'


@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Length'] = str(len(response.get_data()))
    return response


#GET request
@app.route('/data', methods=['GET'])
def get_data():
    try:
        json_data = wlandevices.load_json()
        #logger.info("GET-pyyntö vastaanotettu: \n%s", pformat(json_data))
        return jsonify(json_data), 200
    except Exception as e:
        logger.error(f"Virhe käsitellessä GET-pyyntöä: {e}")
        return jsonify({"error": "Server failed to respond"}), 500


#  post request
@app.route('/receive', methods=['POST'])
def receive_data():
    logger.info("⏳ POST request started")
    if request.method == "OPTIONS":
        return '', 200
    try:
        request_data = request.get_json(force=True)
    except Exception as e:
        logger.error("JSON parsing error: %s", str(e))
        return jsonify({"error": "Invalid JSON"}), 400

    if not request_data:
        logger.error("No data received in POST")
        return jsonify({"error": "Empty payload"}), 400

    try:
        server_data = wlandevices.load_json()
        updates = []


        for key, new_arr in request_data.items():
            # ohitetaan pöydän korkeus
            if key == 'distance_from_floor':
                continue

            # vanha arvo
            old_arr = server_data.get(key)
            if not (isinstance(old_arr, list) and len(old_arr) >= 2):
                continue
            if key not in server_data:
                logger.error(f"Key {key} puuttuu server_data:sta")
                continue
            if not isinstance(server_data[key], list):
                logger.error(f"server_data[{key}] ei ole lista: {server_data[key]}")
                continue
            old_conf = old_arr[1]
            new_conf = new_arr[1]

            if new_conf != old_conf:
                # löydetään laite
                dev = wlandevices.SearchSpecific_device(key, devicesInServer)
                if dev:
                    # lähetetään komento
                    #logger.info("The fucking parameters to controlfromphone funtion: dev %s, new_conf : %s, key: \n%s ",dev, server_data, key )
                    wlandevices.controlFromPhone(dev, server_data, key)
                    updates.append(key)
                    # päivitetään palvelimen JSON‐tila
                    #server_data[key][1] = new_conf
        logger.info("✅ POST response sent")
        return jsonify({"status": "OK"}), 200

    
    except Exception as e:
        logger.error("Error processing POST: %s", str(e))
        return jsonify({"error": "Server failed to respond"}), 500






if __name__ == '__main__':
    #context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logger.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000)