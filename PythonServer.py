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

# Luo Flask-sovellus
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Define the log file
logging.basicConfig(filename="/home/table/Desktop/table2/table_project/flaskserver_log.log",
                    level=logging.INFO, format="%(asctime)s - %(message)s")
BeforeCompare = {}
ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip() # this how we take broker ip address in beging of program-
devicesInServer = broadlink.discover(timeout=5, local_ip_address=ipv4)# lets check devices list '192.168.68.118'

#GET request
@app.route('/data', methods=['GET'])
def get_data():
    json_data = wlandevices.load_json()
    ##height = MC(14, 7)   # toteuta tämä funktio
    ##json_data['distance_from_floor'] = [height]
    #json_data = json.loads(json_data_raw)
    #logging.info(f"GET-pyyntö vastaanotettu: {json_data}")
    #print(f"GET vastaanotettu: {json_data}")
    return jsonify(json_data)

#  post request
@app.route('/receive', methods=['POST'])
def receive_data():
    request_data = request.get_json(force=True)
    if not request_data:
        return jsonify({"error": "Virhe JSON-datan käsittelyssä!"}), 400

    # Ladataan palvelimen versio
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

        old_conf = old_arr[1]
        new_conf = new_arr[1]

        if new_conf != old_conf:
            # löydetään laite
            dev = wlandevices.SearchSpecific_device(key, devicesInServer)
            if dev:
                # lähetetään komento
                wlandevices.controlFromPhone(dev, new_conf, key)
                updates.append(key)
                # päivitetään palvelimen JSON‐tila
                server_data[key][1] = new_conf

    # tallennetaan muutokset levyltä takaisin (jos save_json löytyy)
    try:
        wlandevices.save_json(server_data)
    except AttributeError:
        pass

    return jsonify({"status": "Success", "updated": updates})
# 🔧 **Palvelimen käynnistys**
if __name__ == '__main__':
    context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logging.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000)