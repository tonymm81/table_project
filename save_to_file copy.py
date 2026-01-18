from tkinter import *
import json
import wlan_devices
import motorcontrol
import time
from tkinter import ttk
from typing import List
import os
import logging
from db import save_config, load_config, list_configs 

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


def loadSavedSettingsFromPhone(devices) -> list:
    """
    Palauttaa listan tallennusavaimista (save_key) DB:stä.
    Säilytämme backward compatibilityn: jos DB:ssä ei ole rivejä, yritetään lukea saves.txt.
    """
    try:
        configs = list_configs()  # palauttaa listan dictejä: [{'save_key':..., 'slot_index':..., 'updated_at':...}, ...]
        if configs:
            keys = [row['save_key'] for row in configs]
            logger3.info("Loaded saved configs from DB: %s", keys)
            return keys
        # Fallback: vanha tiedostomekanismi
        path = get_local_path("saves.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                cleanedsamename = json.load(f)
            logger3.info("Loaded saves.txt fallback: %s", cleanedsamename)
            return cleanedsamename
        except FileNotFoundError:
            logger3.warning("No saved configs in DB and saves.txt not found")
            return []
    except Exception as e:
        logger3.error("loadSavedSettingsFromPhone failed: %s", e)
        return []



def load_settings(devices):
    """
    Avaa valintaikkunan ja näyttää tallennusavaimet DB:stä (tai saves.txt fallback).
    Kun käyttäjä valitsee, kutsutaan return_wlan_devices(save_key, devices).
    """
    try:
        # Hae avaimet DB:stä tai fallbackista
        keys = loadSavedSettingsFromPhone(devices)
        # Varmista, että listassa on neljä arvoa (tyhjät paikat jos ei tarpeeksi)
        while len(keys) < 4:
            keys.append("")

        top4 = starting()
        label_1 = Label(top4, text="Choose what setup we load?", font=("helvetica", 10), fg="white", bg="black")
        label_1.grid(row=1, column=1)

        # Käytetään savename‑listaa, jos se on olemassa; muuten keys
        try:
            display_names = keys
        except Exception:
            display_names = ["", "", "", ""]

        # Luo napit, jotka kutsuvat return_wlan_devices(save_key, devices)
        Button(top4, text=str(display_names[0]), fg="white", bg="black", font=("helvetica", 15),
               command=lambda: return_wlan_devices(display_names[0], devices)).grid(row=3, column=1)
        Button(top4, text=str(display_names[1]), fg="white", bg="black", font=("helvetica", 15),
               command=lambda: return_wlan_devices(display_names[1], devices)).grid(row=5, column=1)
        Button(top4, text=str(display_names[2]), fg="white", bg="black", font=("helvetica", 15),
               command=lambda: return_wlan_devices(display_names[2], devices)).grid(row=7, column=1)
        Button(top4, text=str(display_names[3]), fg="white", bg="black", font=("helvetica", 15),
               command=lambda: return_wlan_devices(display_names[3], devices)).grid(row=9, column=1)

        top4.mainloop()
        return
    except Exception as e:
        logger3.error("load_settings failed: %s", e)
        return


def save_settings():
    """
    UI: anna nimi ja valitse slot. Kutsuu get_user_data joka tallentaa DB:hen.
    Tämä funktio ei itse tee DB‑kirjoitusta, vaan delegoi siihen.
    """
    top4 = starting()
    measure = motorcontrol.measure_table()
    listbox = Listbox(top4, width=40, height=10, selectmode=SINGLE)
    listbox.grid(row=15, column=1)
    listbox.insert(1, "save1")
    listbox.insert(2, "save2")
    listbox.insert(3, "save3")
    listbox.insert(4, "save4")
    label_2 = Label(top4, text="Give us name for the saved setup and choose a save slot", font=("helvetica", 10), fg="white", bg="black")
    label_2.grid(row=1, column=1)
    entry = Entry(top4, width=40)
    entry.focus_set()
    entry.grid(row=3, column=1)
    # get_user_data hoitaa DB‑tallennuksen (muista että olet korvannut sen aiemmin)
    save_btn = Button(top4, text="Save changes", fg="white", bg="black", font=("helvetica", 15),
                      command=lambda: get_user_data(listbox, entry, measure))
    save_btn.grid(row=12, column=1)
    top4.mainloop()
    return


# --- Korvattu versio get_user_data_from_phone ---
def get_user_data_from_phone(entry, measure, slot_index):
    """
    Tallentaa nykyisen laitetilan DB:hen avaimella 'entry' ja päivittää slot-listan.
    Alkuperäiset tiedostokirjoitukset on kommentoitu pois.
    """
    try:
        measure_from_floor = "distance_from_floor"
        save_json = wlan_devices.get_json()
        save_json_temp = json.loads(save_json)

        # --- Tiedostokirjoitus (kommentoituna) ---
        # json_path = get_local_path(f"{entry}.json")
        # with open(json_path, "w", encoding="utf-8") as outfile:
        #     json.dump(save_json_temp, outfile, ensure_ascii=False)

        # Tallenna DB:hen (korvattu)
        try:
            save_config(entry, save_json_temp, slot_index)
            logger3.info("Saved config to DB: %s (slot=%s)", entry, slot_index)
        except Exception as e:
            logger3.error("DB save_config failed for %s: %s", entry, e)
            raise

        # Lue vanhat tallennukset (saves.txt) — säilytetään backward compatibility
        saves_path = get_local_path("saves.txt")
        try:
            with open(saves_path, "r", encoding="utf-8") as f:
                savename = json.load(f)
        except FileNotFoundError:
            savename = ["", "", "", ""]
            logger3.warning("saves.txt not found, creating new list")

        # Päivitä oikea slotti
        if isinstance(slot_index, int) and 0 <= slot_index < len(savename):
            savename[slot_index] = entry

        # Päivitä myös saves.txt (kommentoi pois jos haluat poistaa tiedostot käytöstä)
        try:
            with open(saves_path, "w", encoding="utf-8") as file:
                json.dump(savename, file, ensure_ascii=False, indent=2)
        except Exception as e:
            logger3.warning("Failed to update saves.txt: %s", e)

        # Siivoa vanhat tiedostot (jos käytät edelleen UserSettings)
        try:
            cleanUpTheOldUserSaveFiles(savename)
        except Exception as e:
            logger3.warning("cleanUpTheOldUserSaveFiles failed: %s", e)

        return
    except Exception as e:
        logger3.error("error happens in get_user_data_from_phone: %s", e)
        raise




# --- Korvattu versio get_user_data (Tkinter UI) ---
def get_user_data(listbox, entry, measure):
   
    try:
        global savename
        measure_from_floor = "distance_from_floor"
        save_json = wlan_devices.get_json()
        save_json_temp = json.loads(save_json)

        # Hae valittu slot
        saveslot = None
        for i in listbox.curselection():
            saveslot = listbox.index(i)

        if saveslot is None:
            logger3.error("No save slot selected")
            return

        name_file = entry.get() if hasattr(entry, "get") else str(entry)
        logger3.info("Saving slot %s as '%s'", saveslot, name_file)
        savename[saveslot] = str(name_file)

        # Päivitä pöydän korkeus ja laitejson
        desk_level = {measure_from_floor: [measure]}
        save_json_temp.update(desk_level)
        wlan_devices.update_json(save_json_temp)

        # --- Tiedostokirjoitus (kommentoituna) ---
        # json_path = get_local_path(f"{name_file}.json")
        # with open(json_path, "w", encoding="utf-8") as outfile:
        #     json.dump(save_json_temp, outfile, ensure_ascii=False)

        # Tallenna DB:hen
        try:
            save_config(name_file, save_json_temp, saveslot)
            logger3.info("Saved config to DB: %s (slot=%d)", name_file, saveslot)
        except Exception as e:
            logger3.error("DB save_config failed for %s: %s", name_file, e)
            raise

        # Päivitä saves.txt (kommentoi pois myöhemmin jos et halua tiedostoa)
        saves_path = get_local_path("saves.txt")
        try:
            with open(saves_path, "w", encoding="utf-8") as file:
                json.dump(savename, file, ensure_ascii=False, indent=2)
        except Exception as e:
            logger3.warning("Failed to update saves.txt: %s", e)

        # Siivoa vanhat tiedostot (vain jos käytät UserSettings)
        try:
            cleanUpTheOldUserSaveFiles(savename)
        except Exception as e:
            logger3.warning("cleanUpTheOldUserSaveFiles failed: %s", e)

    except Exception as e:
        logger3.error("error happens in get_user_data: %s", e)

    return



def execute_loaded_settings(name: str, index: int, devices: dict):
    """
    Lataa tallennetun asetuksen DB:stä (tai fallback saves.txt) ja suorittaa sen.
    Palauttaa dictin tilasta tai virheestä.
    """
    try:
        # 1) Yritä lukea save_key DB:stä listauksesta, fallback saves.txt jos DB tyhjä
        configs = list_configs()  # palauttaa listan dictejä: [{'save_key':..., 'slot_index':..., 'updated_at':...}, ...]
        if configs:
            # Muodosta lista avaimista ja varmista indeksi
            keys = [row['save_key'] for row in configs]
            if not (0 <= index < len(keys)):
                logger3.error("Invalid slot index %s for DB saved configs", index)
                return {"error": "Invalid slot index"}
            selected_name = keys[index]
            logger3.info("Selected saved config from DB: %s", selected_name)
        else:
            # Fallback: vanha saves.txt -mekanismi
            path = get_local_path("saves.txt")
            try:
                with open(path, "r", encoding="utf-8") as saveNames:
                    savename = json.load(saveNames)
            except FileNotFoundError:
                logger3.error("saves.txt not found and no DB saved configs")
                return {"error": "No saved settings found"}
            if not (0 <= index < len(savename)):
                logger3.error("Invalid slot index %s for saves.txt", index)
                return {"error": "Invalid slot index"}
            selected_name = savename[index]
            logger3.info("Selected saved config from saves.txt fallback: %s", selected_name)

        # 2) Lataa konfiguraatio DB:stä
        loaded_config = load_config(selected_name)
        if loaded_config is None:
            # jos DB:stä ei löydy, yritä vielä tiedostosta (vanha varmistus)
            json_path = get_local_path(f"{selected_name}.json")
            try:
                with open(json_path, "r", encoding="utf-8") as SavedSettingsJsonFile:
                    loaded_config = json.load(SavedSettingsJsonFile)
                logger3.warning("Loaded config from file fallback: %s", selected_name)
            except FileNotFoundError:
                logger3.error("Saved configuration not found in DB or file for key %s", selected_name)
                return {"error": "Saved configuration not found"}

        # 3) Hae nykyinen laitetila ja suorita asetukset
        current_devices = json.loads(wlan_devices.get_json())
        try:
            return_wlan_devices_from_phone(loaded_config, current_devices, devices)
        except Exception as e:
            logger3.exception("Error while executing loaded settings %s: %s", selected_name, e)
            return {"error": "Failed to execute settings"}

        return {"status": f"Settings '{selected_name}' executed"}
    except Exception as e:
        logger3.exception("execute_loaded_settings unexpected error: %s", e)
        return {"error": "Server error"}



def return_wlan_devices(saveslot, devices): # here we open new and saved json and measure table distance from loaded json value
    #wlan_devices.update_json(devices)
    progress = IntVar()
    level = DoubleVar()
    new_json = wlan_devices.get_json() # this is new. based on start time
    new_json_temp = json.loads(new_json) # loads convert to python dictonary and load only json string.
    size = len(saveslot)
    saveslot_temp = saveslot[:size -1]#lets delete newline
    
    with open(f'{saveslot_temp}.json') as json_file:
        saved_json = json.load(json_file)
        #saved_json = json.loads(saved_jsontemp)#gives an wrong value error


    json_file.close()
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
                            #else:
        
                                #print("not changes on lights", saved_json[device_saved][1]['pwr'], new_json_temp[x][1]['pwr'])
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

