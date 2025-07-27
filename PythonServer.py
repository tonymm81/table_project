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
    try:
        request_data = request.get_json(force=True) or {}
        logger.info("post data %s", request_data)
    except Exception as e:
        logger.error("JSON parsing error: %s", e)
        return jsonify({"error": "Invalid JSON"}), 400

    if not request_data:
        return jsonify({"error": "Empty payload"}), 400
    try:
        server_data = wlandevices.load_json()
        updates = []

        for key, new_arr in request_data.items():
            if key == 'distance_from_floor':
                continue

            old_arr = server_data.get(key)
            if not (isinstance(old_arr, list) and len(old_arr) >= 2):
                continue

            old_cfg = old_arr[1]
            new_cfg = new_arr[1]
            logger.info("old_conf for %s: %s", key, old_cfg)
            logger.info("new_conf for %s: %s", key, new_cfg)

            # Etsi laiteolio
            dev = wlandevices.SearchSpecific_device(key, devicesInServer)
            if not dev:
                logger.error("Device not found: %s", key)
                continue

            # 1) Virrankytkentä
            if isinstance(new_cfg, bool):
                if new_cfg != old_cfg:
                    logger.info(f"Toggling power for {key} → {new_cfg}")
                    wlandevices.controlFromPhone(dev, server_data, key)
                    server_data[key][1] = new_cfg
                    updates.append(key)
                # siirry seuraavaan avaimeseen
                continue

            # 2) Palauta uuden konfigin objektina
            if not isinstance(new_cfg, dict):
                continue

            # 3) PWR-arvo dictissä
            p_old = old_cfg.get('pwr')
            p_new = new_cfg.get('pwr', p_old)
            if p_new != p_old:
                logger.info(f"Toggling power for {key} → {p_new}")
                wlandevices.controlFromPhone(dev, server_data, key)
                server_data[key][1]['pwr'] = p_new
                updates.append(key)

            # 4) Brightness
            b_old = old_cfg.get('brightness')
            b_new = new_cfg.get('brightness', b_old)
            if b_new != b_old:
                logger.info(f"Brightness change for {key}: {b_old} → {b_new}")
                wlandevices.SetPulpStateFromPhone(dev, b_new, None, mode='brightness')
                server_data[key][1]['brightness'] = b_new
                updates.append(key)

            # 5) Bulb color mode
            cm_old = old_cfg.get('bulb_colormode')
            cm_new = new_cfg.get('bulb_colormode', cm_old)
            if cm_new != cm_old:
                logger.info(f"Color mode change for {key}: {cm_old} → {cm_new}")
                wlandevices.SetPulpStateFromPhone(dev, None, cm_new, mode='colormode')
                server_data[key][1]['bulb_colormode'] = cm_new
                updates.append(key)

            # 6) Color temperature (Kelvin)
            ct_old = old_cfg.get('colortemp')
            ct_new = new_cfg.get('colortemp', ct_old)
            if ct_new != ct_old:
                logger.info(f"Color temp change for {key}: {ct_old} → {ct_new}")
                wlandevices.SetPulpStateFromPhone(dev, None, None, mode='colortemp', temp=ct_new)
                server_data[key][1]['colortemp'] = ct_new
                updates.append(key)

        # Kirjoita JSON vain, jos jotain päivittyi
        if updates:
            wlandevices.update_json(server_data)
            logger.info("✅ Updated JSON for keys %s", updates)

        return jsonify({"status": "OK", "updated": updates}), 200

    except Exception as e:
        logger.error("Error processing POST: %s", e)
        return jsonify({"error": "Server error"}), 500




if __name__ == '__main__':
    #context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logger.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000)