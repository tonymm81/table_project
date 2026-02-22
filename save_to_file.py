from tkinter import *
import json
import wlan_devices
import motorcontrol
import time
from tkinter import ttk
from typing import List
import os
import logging
from db import save_config, list_configs, load_config# version 133 changes

savenumber = 0
savename = ["save1", "save2", "save3", "save4"] # this we will save to file. This how we know what name of json file we are looking for..

logger3 = logging.getLogger("Save_to_file")
file_handler = logging.FileHandler("/home/table/Desktop/table2/table_project/logs/Save_to_file.log")
formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler.setFormatter(formatter)
logger3.setLevel(logging.WARNING)
logger3.addHandler(file_handler)
if not logger3.hasHandlers():
    logger3.addHandler(file_handler)

logger3.info("Logger käynnistetty onnistuneesti.")

def get_local_path(filename):
    user_settings_dir = os.path.join(os.getcwd(), "UserSettings")
    os.makedirs(user_settings_dir, exist_ok=True)  # Luo kansio tarvittaessa
    return os.path.join(user_settings_dir, filename)


def starting():
    top4 = Toplevel()
    top4.title("Save or load settings")
    top4.geometry("800x500")
    top4.configure(background="black")
    exit_btn = Button(top4, text="Exit",fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 22, column=1)
    return top4


def loadSavedSettingsFromPhone(devices) -> List[str]:# version 133 changes
    try:
        rows = list_configs()  # palauttaa listan tupleja: (save_key, slot_index, updated_at)

        if not rows:
            return []  # sama kuin tyhjä tiedosto

        # Poimitaan vain tallennusnimet (save_key)
        save_names = [row[0] for row in rows]

        # Palautetaan max 4 tallennusta, kuten ennenkin
        return save_names[:4]

    except Exception as e:
        logger3.error(f"Failed to load saved settings from DB: {e}")
        return []





def load_settings(devices):# version 133 changes
    try:
        # Hae tallennusnimet kannasta
        rows = list_configs()  # [(save_key, slot_index, updated_at), ...]

        if not rows:
            logger3.error("No saved settings found in DB")
            return

        # Poimitaan tallennusnimet
        save_names = [row[0] for row in rows]
        save_names = save_names[:4]  # max 4 slottia

    except Exception as e:
        logger3.error(f"Failed to load saved settings from DB: {e}")
        return

    # --- UI alkaa tästä ---
    top4 = starting()
    Label(
        top4,
        text="Choose what setup we load?",
        font=("helvetica", 10),
        fg="white",
        bg="black"
    ).grid(row=1, column=1)

    # Luo 4 nappia dynaamisesti
    for i in range(4):
        name = save_names[i] if i < len(save_names) else ""
        Button(
            top4,
            text=name,
            fg="white",
            bg="black",
            font=("helvetica", 15),
            command=lambda n=name: return_wlan_devices(n, devices)
        ).grid(row=3 + i*2, column=1)

    top4.mainloop()



def save_settings(): # version 133 changes 
    top4 = starting()
    measure = motorcontrol.measure_table()

    listbox = Listbox(top4, width=40, height=10, selectmode=SINGLE)
    listbox.grid(row=15, column=1)
    listbox.insert(1, "save1")
    listbox.insert(2, "save2")
    listbox.insert(3, "save3")
    listbox.insert(4, "save4")

    Label(
        top4,
        text="Give us name for the saved setup and choose a save slot",
        font=("helvetica", 10),
        fg="white",
        bg="black"
    ).grid(row=1, column=1)

    entry = Entry(top4, width=40)
    entry.focus_set()
    entry.grid(row=3, column=1)

    Button(
        top4,
        text="Save changes",
        fg="white",
        bg="black",
        font=("helvetica", 15),
        command=lambda: save_user_settings_from_tk(listbox, entry, measure)
    ).grid(row=12, column=1)

    top4.mainloop()





def get_user_data_from_phone(entry, measure, slot_index):# version 133 changes
    try:
        # 1. Hae tämänhetkinen devices-tila (snapshot)
        devices_snapshot = wlan_devices.load_json_from_db()  # palauttaa dictin {device_key: {...}}
        save_config(
            save_key=entry,
            value=devices_snapshot,
            slot_index=slot_index
        )
        return

    except Exception as e:
        logger3.error(f"Error saving user settings to DB: {e}")






def save_user_settings_from_tk(listbox, entry, measure):# version 133 changes
    try:
        # 1. Selvitä valittu tallennuspaikka (0–3)
        selection = listbox.curselection()
        if not selection:
            logger3.error("No save slot selected")
            return

        slot_index = selection[0]  # 0–3

        # 2. Käyttäjän antama tallennusnimi
        save_key = entry.get().strip()
        if not save_key:
            logger3.error("No save name entered")
            return

        # 3. Hae tämänhetkinen devices-snapshot
        devices_snapshot = wlan_devices.load_json_from_db()

        # 4. Lisää measure snapshotin sisään (kuten vanha logiikka)
        devices_snapshot["distance_from_floor"] = [measure]

        # 5. Tallenna snapshot kantaan
        save_config(
            save_key=save_key,
            value=devices_snapshot,
            slot_index=slot_index
        )

        logger3.info(f"Saved settings '{save_key}' to slot {slot_index}")

    except Exception as e:
        logger3.error(f"Error saving settings from Tkinter: {e}")





def execute_loaded_settings(name: str, index: int, devices: dict):# version 133 changes
    try:
        # 1. Hae tallennuslista kannasta
        rows = list_configs()  # [(save_key, slot_index, updated_at), ...]

        if not rows:
            return {"error": "No saved settings found"}

        # 2. Poimi tallennusnimet listaksi
        save_names = [row[0] for row in rows]

        # 3. Tarkista indeksi
        if not (0 <= index < len(save_names)):
            return {"error": "Invalid slot index"}

        selected_name = save_names[index]
        logger3.info(f"Valittu asetuksen nimi: {selected_name}")

        # 4. Lataa snapshot kannasta
        loaded_config = load_config(selected_name)
        if loaded_config is None:
            return {"error": "Saved configuration not found"}

        # 5. Hae nykyinen devices-tila
        current_devices = json.loads(wlan_devices.get_json())

        # 6. Sovella snapshot
        return_wlan_devices_from_phone(loaded_config, current_devices, devices)

        return {"status": f"Settings '{selected_name}' executed"}

    except Exception as e:
        logger3.error(f"Error loading settings: {e}")
        return {"error": "Failed to load settings"}



def return_wlan_devices(saveslot, devices): # here we open new and saved json and measure table distance from loaded json value
    #wlan_devices.update_json(devices)
    progress = IntVar()
    level = DoubleVar()
    new_json = wlan_devices.get_json() # this is new. based on start time
    new_json_temp = json.loads(new_json) # loads convert to python dictonary and load only json string.
    #size = len(saveslot)
    #saveslot_temp = saveslot[:size -1]#lets delete newline
      
    saved_json = load_config(saveslot) 
    if saved_json is None: 
        logger3.error(f"No saved config found for key: {saveslot}") 
        return
    #with open(f'{saveslot_temp}.json') as json_file:
        #saved_json = json.load(json_file)
        #saved_json = json.loads(saved_jsontemp)#gives an wrong value error


    #json_file.close()
    try:
        rootloading = Toplevel()
        rootloading.title("Loading settings")
        progressbar = ttk.Progressbar(rootloading, mode="indeterminate")
        progressbar.place(x=30, y=60, width=200)
        rootloading.geometry("300x200")
        progressbar.start()
        rootloading.update()
        progressbar.update()
        print("what now again saved: ", saved_json["distance_from_floor"][0], "this moment", new_json_temp["distance_from_floor"][0] )
        if float(saved_json["distance_from_floor"][0]) > float(new_json_temp["distance_from_floor"][0]): # lets adjust table up
            max_distance = saved_json["distance_from_floor"][0] - new_json_temp["distance_from_floor"][0] 
            level.set(max_distance)
            print("motor up", saved_json["distance_from_floor"][0], new_json_temp["distance_from_floor"][0], max_distance)
            motorcontrol.motor_control(level,  15, 23)
            print("motor up", saved_json["distance_from_floor"][0], new_json_temp["distance_from_floor"][0], max_distance)            
            rootloading.update()
            progressbar.update()


        if float(saved_json["distance_from_floor"][0]) < float(new_json_temp["distance_from_floor"][0]):# lets adjust table down
            max_distance = new_json_temp["distance_from_floor"][0] - saved_json["distance_from_floor"][0] 
            level.set(max_distance)
            motorcontrol.motor_control( level, 12, 8)
            print("motor down", saved_json["distance_from_floor"][0], new_json_temp["distance_from_floor"][0], max_distance)
            rootloading.update()
            progressbar.update()
        # here we will check the wlan devices state and turn on or off comparing saved settings
        for device_saved in saved_json:
            time.sleep(0.2)
           
            rootloading.update()
            progressbar.update()
            #print("what data outer loop", device_saved)
            for x in new_json_temp:
                time.sleep(0.2)
                #print("what data in inner loop", x)
                if device_saved != "distance_from_floor":
                    if device_saved == x:
                        #print("Same device:", device_saved)
                        if (saved_json[device_saved][2] == 32000 or saved_json[device_saved][2] == 42348  or saved_json[device_saved][2] == 30073):
                            if saved_json[device_saved][1] != new_json_temp[x][1]:
                                #print("Change plug state:", saved_json[device_saved][1], new_json_temp[x][1])
                                wlan_devices.control_wlan_devices(device_saved, devices)
                            #else:
                                #print("same state", saved_json[device_saved][1],new_json_temp[x][1])
                        if (saved_json[device_saved][2] == 24686):
                            #if saved_json[device_saved][1] == 
                            if saved_json[device_saved][1]['pwr'] != new_json_temp[x][1]['pwr']:
                                control = wlan_devices.SearchSpecific_device(device_saved, devices)
                                #print("Change bulb state:", saved_json[device_saved][1]['pwr'], new_json_temp[x][1]['pwr'])
                                wlan_devices.set_state_bulp(new_json_temp, device_saved, control, "pwr", 0)
                            #else:
        
                                #print("not changes on lights", saved_json[device_saved][1]['pwr'], new_json_temp[x][1]['pwr'])
    except Exception as e:
        print("wlan devices control fails on error : ", e)  
        logger3.error("wlan devices control fails on error : %s", e)  

    progressbar.stop()
    rootloading.destroy()
    progressbar.destroy()       
    return


def return_wlan_devices_from_phone(loaded_config, current_devices, devices): # here we open new and saved json and measure table distance from loaded json value
    
    try:
        #print("what now again saved: ", saved_json["distance_from_floor"][0], "this moment", new_json_temp["distance_from_floor"][0] )
        if float(loaded_config["distance_from_floor"][0]) > float(current_devices["distance_from_floor"][0]): # lets adjust table up
            max_distance = loaded_config["distance_from_floor"][0] - current_devices["distance_from_floor"][0] 
            print("motor up", loaded_config["distance_from_floor"][0], current_devices["distance_from_floor"][0], max_distance)
            motorcontrol.motorControlFromPhone(max_distance,  15, 23)
            print("motor up", loaded_config["distance_from_floor"][0], current_devices["distance_from_floor"][0], max_distance)            
            


        if float(loaded_config["distance_from_floor"][0]) < float(current_devices["distance_from_floor"][0]):# lets adjust table down
            max_distance = current_devices["distance_from_floor"][0] - loaded_config["distance_from_floor"][0] 
            motorcontrol.motorControlFromPhone( max_distance, 12, 8)
            print("motor down", loaded_config["distance_from_floor"][0], current_devices["distance_from_floor"][0], max_distance)
        # here we will check the wlan devices state and turn on or off comparing saved settings
        for device_saved in loaded_config:
            time.sleep(0.2)           
            #print("what data outer loop", device_saved)
            for x in current_devices:
                try:
                    time.sleep(0.2)
                    #print("what data in inner loop", x)
                    if device_saved != "distance_from_floor":
                        if device_saved == x:
                            #print("Same device:", device_saved)
                            if (loaded_config[device_saved][2] == 32000 or loaded_config[device_saved][2] == 42348  or loaded_config[device_saved][2] == 30073):
                                if loaded_config[device_saved][1] != current_devices[x][1]:
                                    #print("Change plug state:", saved_json[device_saved][1], new_json_temp[x][1])
                                    wlan_devices.control_wlan_devices(device_saved, devices)
                                #else:
                                    #print("same state", saved_json[device_saved][1],new_json_temp[x][1])
                            if (loaded_config[device_saved][2] == 24686):
                                #if saved_json[device_saved][1] == 
                                if loaded_config[device_saved][1]['pwr'] != current_devices[x][1]['pwr']:
                                    control = wlan_devices.SearchSpecific_device(device_saved, devices)
                                    #print("Change bulb state:", saved_json[device_saved][1]['pwr'], new_json_temp[x][1]['pwr'])
                                    wlan_devices.set_state_bulp(current_devices, device_saved, control, "pwr", 0)
                
                except Exception as e:
                    logger3.error("Some devices were not found : %s", e)
                                    #else:
            
    except Exception as e:
        print("wlan devices control fails on error : ", e)  
        logger3.error("wlan devices control fails on error : %s", e)     
    return


def cleanUpTheOldUserSaveFiles(savename : list):
    user_settings_dir = os.path.join(os.getcwd(), "UserSettings")
    try:
        # find all of the UserSettings files
        all_files = os.listdir(user_settings_dir)
        json_files = [f for f in all_files if f.endswith(".json")]

        # List for allowed save names
        allowed_files = [f"{name}.json" for name in savename if name]

        # delete the files, what are not needed
        for json_file in json_files:
            if json_file not in allowed_files:
                full_path = os.path.join(user_settings_dir, json_file)
                os.remove(full_path)
                logger3.info(f"Poistettiin vanha asetustiedosto: {json_file}")
    except Exception as e:
        logger3.error(f"Virhe poistettaessa vanhoja tiedostoja: {e}")