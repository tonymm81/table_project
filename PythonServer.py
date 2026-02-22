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
from motorcontrol import motorControlFromPhone
from pprint import pformat
import save_to_file as saved
from subprocess import call
import threading#version 130
import time#version 130
#from table_project.table_project.OldFiles.dbOldWorking import get_connection
import traceback
traceback.print_exc()

logging.raiseExceptions = True

# Luo Flask-sovellus
app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, supports_credentials=True)

cached_devices = [] 
cached_devices_lock = threading.Lock()

# Define the log file
logger = logging.getLogger("pythonserver")
file_handler = logging.FileHandler("/home/table/Desktop/table2/table_project/logs/flaskserver_log.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)
logger.setLevel(logging.ERROR)
logger.addHandler(file_handler)

#print("PYTHONSERVER USING:", wlandevices.__file__) 
#print("JSON_FILE AT START:", wlandevices.JSON_FILE)


BeforeCompare = {}
ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip() # this how we take broker ip address in beging of program-
devicesInServer = broadlink.discover(timeout=5, local_ip_address=ipv4)# lets check devices list 

def db_load_devices(): # this can be deleted
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT device_key, value_json FROM devices")
    rows = cur.fetchall()
    conn.close()

    result = {}
    for key, value_json in rows:
        result[key] = json.loads(value_json)
    return result


def db_save_devices(data: dict):# this can be deleted
    conn = get_connection()
    cur = conn.cursor()
    for key, value in data.items():
        cur.execute(
            "REPLACE INTO devices (device_key, value_json) VALUES (%s, %s)",
            (key, json.dumps(value))
        )
    conn.commit()
    conn.close()




@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Length'] = str(len(response.get_data()))
    return response


#GET request
@app.route('/data', methods=['GET'])# get the wlan devices status and return it to react native
def get_data():
    try:
        json_data = wlandevices.load_json_from_db()
        #logger.info("GET-pyyntö vastaanotettu: \n%s", pformat(json_data))
        return jsonify(json_data), 200
    except Exception as e:
        logger.error(f"Virhe käsitellessä GET-pyyntöä: {e}")
        return jsonify({"error": "Server failed to respond"}), 500
    

@app.route('/SavedSettings', methods=['GET'])  # version 126. This returns user saved settings to react native
def get_SavedSettings():
    try:
        ReturnSavedSettings = saved.loadSavedSettingsFromPhone(devicesInServer)
        return jsonify(ReturnSavedSettings), 200
    except Exception as e:
        logger.error(f"Virhe käsitellessä GET-pyyntöä: {e}")
        return jsonify({"error": "Server failed to respond"}), 500
    

@app.route('/ShutDownPythonServer', methods=['GET']) # shutdown the python server from phone
def ShutDown():
    try:
        call("sudo shutdown -h now", shell=True)
    except Exception as e:
        logger.error(f"Error, happend when tryiong to shut down: {e}")
        return  jsonify({"error": "Server failed to respond {e}"}), 500
    

def UpdateTheDevicesJson(): #version 130
    try: 
        threading.Thread(target=background_update).start() 
        return jsonify({"status": "started"}), 200 
    except Exception as e: 
        return jsonify({"error": str(e)}), 500
    
#  post request    
@app.route('/SaveSettingsFromPhone', methods=['POST'])  # version 127 save the settings from react native
def saveUserSettings():
    logger.debug("savesettings post arrived")
    try:
        data = request.get_json()
        entry = data.get("entry")
        measure = data.get("measure")
        slot_index = data.get("slotIndex") 

        saved.get_user_data_from_phone(entry, measure, slot_index)  
        return jsonify({"status": "Settings saved"}), 200
    except Exception as e:
        logger.error(f"Virhe käsitellessä POST-pyyntöä: {e}")
        return jsonify({"error": "Server failed to respond"}), 500


@app.route('/LoadSettingsFromPhone', methods=['POST'])# this route will activate the loaded settings
def loadUserSettings():
    try:
        data = request.get_json()
        name = data.get("name")
        index = data.get("index")
        result = saved.execute_loaded_settings(name, index, devicesInServer)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Virhe käsitellessä POST-pyyntöä: {e}")
        return jsonify({"error": "Server failed to respond"}), 500


@app.route('/receive', methods=['POST'])# in this route, we handle the wlan lamps, wlan sockets and electric table level
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
        server_data = wlandevices.load_json_from_db()
        updates = []

        if 'distance_from_floor' in request_data:  # update to version 125
            requested_height = request_data['distance_from_floor']
            if isinstance(requested_height, list):
                requested_height = requested_height[0]

            current_height = wlandevices.measure_table()
            logger.info(f"📏 Current height: {current_height} cm, Requested: {requested_height} cm")
            difference = 0
            if abs(current_height - requested_height) > 0.5:  # tolerance.
                if requested_height > current_height:
                    difference = requested_height - current_height
                    logger.info(f" Requested height is higher → motor_control('up', {requested_height})")
                    motorControlFromPhone(difference, 15, 23)
                elif requested_height < current_height:
                    difference = current_height - requested_height
                    logger.info(f" Requested height is lower → motor_control('down', {requested_height})")
                    motorControlFromPhone(difference, 12, 8)

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

            # ennen: fresh_devices = broadlink.discover(timeout=5, local_ip_address=ipv4)
            # sen sijaan:
            try:
                cached_devices_lock.acquire()
                fresh_devices = list(cached_devices)  # kopioidaan käyttöä varten
            finally:
                cached_devices_lock.release()

            # fallback jos cache tyhjä (esim. käynnistyksen aikana)
            if not fresh_devices:
                try:
                    fresh_devices = broadlink.discover(timeout=3, local_ip_address=ipv4)
                    logger.info("Fallback discover used in receive_data")
                except Exception as e:
                    logger.error("Fallback discover failed: %s", e)
                    fresh_devices = []

            dev = wlandevices.SearchSpecific_device(key, fresh_devices)
            if not dev:
                logger.error("Device not found: %s", key)
                continue

            # power on or off
            if isinstance(new_cfg, bool):
                if new_cfg != old_cfg:
                    logger.info(f"Toggling power for {key} → {new_cfg}")
                    wlandevices.controlFromPhone(dev, server_data, key)
                    server_data[key][1] = new_cfg
                    updates.append(key)
                #continue to next key
                continue

            #  return new config
            if not isinstance(new_cfg, dict):
                continue

            # PWR-value  in dict
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
                wlandevices.SetPulpStateFromPhone(dev,None, None, mode='colortemp', temp=ct_new)
                server_data[key][1]['colortemp'] = ct_new
                updates.append(key)

        # Update json only if it has changed
        if updates:
            wlandevices.save_json_to_db(server_data)
            logger.info(" Updated JSON for keys %s", updates)

        return jsonify({"status": "OK", "updated": updates}), 200

    except Exception as e:
        logger.error("Error processing POST: %s", e)
        return jsonify({"error": "Server error"}), 500


@app.route('/PairNewDevice', methods=['POST'])#version 130
def pair_new_device():
    logger.info("PairNewDevice POST arrived")
    try:
        data = request.get_json(force=True) or {}
        ssid = data.get("ssid")
        password = data.get("password")

        if not ssid or not password:
            logger.error("Missing ssid or password in payload")
            return jsonify({"error": "Missing ssid or password"}), 400

        logger.info(f"Starting Broadlink setup for SSID: {ssid}")

        # 1) Käynnistä Broadlink-paritus: lähetä WiFi-tiedot laitteelle
        #   (joissain versioissa on myös argumentti 'security_mode', mutta
        #   ssid, password on perusjuttu)
        broadlink.setup(ssid, password)

        # 2) Odota hetki, että laite liittyy verkkoon ja löydetään se
        #    käytetään samaa ipv4-osoitetta kuin muuallakin
        devices = broadlink.discover(timeout=10, local_ip_address=ipv4)

        if not devices:
            logger.warning("No devices found after pairing")
            return jsonify({"status": "NO_DEVICES_FOUND"}), 200

        # Muutetaan löydetyt laitteet serialisoitavaan muotoon
        result = []
        for dev in devices:
            try:
                host = None
                if isinstance(dev.host, tuple):
                    host = dev.host[0]
                else:
                    host = dev.host

                result.append({
                    "host": host,
                    "mac": ":".join(["%02X" % b for b in dev.mac]) if getattr(dev, "mac", None) else None,
                    "devtype": getattr(dev, "devtype", None),
                    "type": dev.__class__.__name__
                })
            except Exception as e:
                logger.error(f"Error serializing device: {e}")

        logger.info("Pairing result: %s", pformat(result))

        # Halutessa voisi myös päivittää devicesInServer globaalin listan:
        # global devicesInServer
        # devicesInServer = devices

        return jsonify({"status": "OK", "devices": result}), 200

    except Exception as e:
        logger.error(f"Error in PairNewDevice: {e}")
        return jsonify({"error": "Server failed to pair device"}), 500


def background_update(): #version 130
    fresh = broadlink.discover(timeout=5, local_ip_address=ipv4)
    temp_json = wlandevices.check_wlan_device_status(fresh)
    wlandevices.persist_devices(temp_json)
    print("Device list updated")
    
    
def auto_update_loop():
    global cached_devices
    while True:
        try:
            fresh = broadlink.discover(timeout=5, local_ip_address=ipv4)
            logger.info("Auto-update: discover returned %d devices, calling check_wlan_device_status()", len(fresh))
            temp_json = wlandevices.check_wlan_device_status(fresh)
            # persistataan
            wlandevices.persist_devices(temp_json)
            logger.info("Auto-update: check_wlan_device_status() finished in s, returned %d entries", len(temp_json))
            # päivitetään cache thread-safe
            try:
                cached_devices_lock.acquire()
                cached_devices = fresh  # tallennetaan Broadlink‑objektit
            finally:
                cached_devices_lock.release()

            logger.info("Auto-update: devices refreshed, cached_devices updated")
        except Exception as e:
            logger.error("Auto-update error: %s", e)
            import traceback; traceback.print_exc()
        time.sleep(280)



if __name__ == '__main__':
    threading.Thread(target=auto_update_loop, daemon=True).start()#version 130
    #context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logger.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000)