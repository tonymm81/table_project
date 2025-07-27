@app.route('/receive', methods=['POST'])
def receive_data():
    logger.info("⏳ POST request started")

    try:
        request_data = request.get_json(force=True)
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
            # ohitetaan ei-kiinnostavat kentät
            if key == 'distance_from_floor':
                continue

            old_arr = server_data.get(key)
            if not (isinstance(old_arr, list) and len(old_arr) >= 2):
                continue

            old_conf = old_arr[1]
            new_conf = new_arr[1]
            logger.info("old_conf for %s: %s", key, old_conf)
            logger.info("new_conf for %s: %s", key, new_conf)

            # 1) Virrankytkentä (boolean)
            if isinstance(new_conf, bool):
                if new_conf != old_conf:
                    dev = wlandevices.SearchSpecific_device(key, devicesInServer)
                    if dev:
                        logger.info(f"Toggling power for {key} → {new_conf}")
                        wlandevices.controlFromPhone(dev, server_data, key)
                        server_data[key][1] = new_conf
                        updates.append(key)
                continue

            # 2) Sanakirja‐asetukset: kirkkaus, värimoodi, pwr yms.
            if not isinstance(new_conf, dict):
                logger.error(f"Unexpected config type for {key}: {type(new_conf)}")
                continue

            # Tarkistetaan pwr-muutos
            pwr_old = old_conf.get('pwr')
            pwr_new = new_conf.get('pwr', pwr_old)
            dev = wlandevices.SearchSpecific_device(key, devicesInServer)
            if pwr_new != pwr_old:
               
                if dev:
                    logger.info(f"Toggling power for {key} → {pwr_new}")
                    wlandevices.controlFromPhone(dev, server_data, key)
                    server_data[key][1]['pwr'] = pwr_new
                    updates.append(key)

            elif (
                
                ('brightness' in new_conf and new_conf['brightness'] != old_conf.get('brightness'))
               
                 ):
                 if dev:
                    br = new_conf.get('brightness', old_conf['brightness'])
                    cm = new_conf.get('bulb_colormode', old_conf['bulb_colormode'])
                    logger.info(f"Setting lamp {key} brightness={br}, bulb_colormode={cm}")
                    
                    # 1) Lähetä komento laitteelle
                    wlandevices.SetPulpStateFromPhone(dev, br, cm, 1)
                    server_data[key][1]['brightness']     = br
                    server_data[key][1]['bulb_colormode'] = cm
                    
                    # 3) Merkitse päivitys listaan
                    updates.append(key)
            elif (
                 ('bulb_colormode' in new_conf and new_conf['bulb_colormode'] != old_conf.get('bulb_colormode'))
                 ):
                     if dev:
                        br = new_conf.get('brightness', old_conf['brightness'])
                        cm = new_conf.get('bulb_colormode', old_conf['bulb_colormode'])
                        logger.info(f"Setting lamp {key} brightness={br}, bulb_colormode={cm}")   
                        wlandevices.SetPulpStateFromPhone(dev, br, cm, 2) 
                        server_data[key][1]['brightness']     = br
                        server_data[key][1]['bulb_colormode'] = cm
                    
                    # 3) Merkitse päivitys listaan
                        updates.append(key)    
                    # 2) Päivitä server_data–rakenne
                   

        if updates:
            wlandevices.update_json(server_data)
            logger.info(f"✅ Updated JSON for keys {updates}")

        return jsonify({"status": "OK", "updated": updates}), 200

    except Exception as e:
        logger.error("Error processing POST: %s", e)
        return jsonify({"error": "Server error"}), 500