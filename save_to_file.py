from tkinter import *
import json
import wlan_devices
import motorcontrol
import time
from tkinter import ttk
from typing import List
import os
import logging


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


def loadSavedSettingsFromPhone(devices) -> List[str]:
    try:
        path = get_local_path("saves.txt")
        logger3.info(f"Path, where we try to open file: {path}")

        with open(path, "r", encoding="utf-8") as f:
            cleanedsamename = json.load(f)
        logger3.info(f"What we loaded: {cleanedsamename}")
        f.close()
        return cleanedsamename
    except FileNotFoundError:
         logger3.error("saves.txt did not found")
         return


def load_settings(devices):
    try:
        global savename
        path = get_local_path("saves.txt")
        with open(path, "r", encoding="utf-8") as f:
            cleanedsamename = json.load(f)
        f.close()  
    except FileNotFoundError:
        logger3.error("saves.txt did not found")
        return
      
    top4 = starting()
    label_1 = Label(top4, text= "Choose what setup we load?", font=("helvetica", 10), fg="white", bg="black")
    label_1.grid(row=1, column=1)
    load_json = wlan_devices.get_json()
    load_btn1 = Button(top4, text=str(cleanedsamename[0]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[0], devices)).grid(row = 3, column=1)
    load_btn2 = Button(top4, text=str(cleanedsamename[1]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[1], devices)).grid(row = 5, column=1)
    load_btn3 = Button(top4, text=str(cleanedsamename[2]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[2], devices)).grid(row = 7, column=1)
    load_btn4 = Button(top4, text=str(cleanedsamename[3]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[3], devices)).grid(row = 9, column=1)
    top4.mainloop()
    return


def save_settings():
    top4 = starting()
    measure = motorcontrol.measure_table()
    listbox = Listbox(top4, width=40, height=10, selectmode=SINGLE)
    listbox.grid(row=15, column=1)
    listbox.insert(1, "save1")
    listbox.insert(2, "save2")
    listbox.insert(3, "save3")
    listbox.insert(4, "save4")
    label_2 = Label(top4, text= "Give us name for the saved setup and choose a save slot", font=("helvetica", 10), fg="white", bg="black")
    label_2.grid(row=1, column=1)
    entry= Entry(top4, width= 40)
    entry.focus_set()
    entry.grid(row=3, column=1)
    save_btn = Button(top4, text="Save changes",fg="white", bg="black",font=("helvetica", 15), command=lambda: get_user_data(listbox, entry, measure)).grid(row = 12, column=1)
    #string= entry.get() when ok button pressed
    top4.mainloop()
    return

def get_user_data_from_phone(entry, measure, slot_index): # this funktion will saved the devices.json wiht user given name and saves user given save name to saves.txt also
    try:
        measure_from_floor = "distance_from_floor"
        save_json = wlan_devices.get_json()
        save_json_temp = json.loads(save_json)

        # Save the json file
        json_path = get_local_path(f"{entry}.json")
        with open(json_path, "w", encoding="utf-8") as outfile:
            json.dump(save_json_temp, outfile, ensure_ascii=False)

        # Lue vanhat tallennukset
        saves_path = get_local_path("saves.txt")
        try:
            with open(saves_path, "r", encoding="utf-8") as f:
                savename = json.load(f)
        except FileNotFoundError:
            savename = ["", "", "", ""]
            logger3.error("saves.txt did not found")
        # Päivitä oikea slotti
        if isinstance(slot_index, int) and 0 <= slot_index < len(savename):
            savename[slot_index] = entry

        # Tallenna takaisin
        with open(saves_path, "w", encoding="utf-8") as file:
            json.dump(savename, file, ensure_ascii=False, indent=2)
        cleanUpTheOldUserSaveFiles(savename)
        outfile.close()
        file.close()
        return
    except Exception as e:
        logger3.error("error happens in filehandling %s", e)



def get_user_data(listbox, entry, measure): # this funktion will saved the devices.json wiht user given name and saves user given save name to saves.txt also
    try:
        global savename
        measure_from_floor = "distance_from_floor"
        save_json = wlan_devices.get_json()
        save_json_temp = json.loads(save_json)

        for i in listbox.curselection():
            saveslot = listbox.index(i)

        name_file = entry.get()
        print("test", name_file, saveslot)
        savename[saveslot] = str(name_file)

        desk_level = {measure_from_floor: [measure]}
        save_json_temp.update(desk_level)
        wlan_devices.update_json(save_json_temp)

        json_path = get_local_path(f"{name_file}.json")
        with open(json_path, "w", encoding="utf-8") as outfile:
            json.dump(save_json_temp, outfile, ensure_ascii=False)

        saves_path = get_local_path("saves.txt")
        with open(saves_path, "w", encoding="utf-8") as file:
            json.dump(savename, file, ensure_ascii=False, indent=2)
        cleanUpTheOldUserSaveFiles(savename)
        outfile.close()
        file.close()
    except Exception as e:
        logger3.error("error happens in filehandling %s", e)

    return


def execute_loaded_settings(name: str, index: int, devices : dict):#version 127 This will load the wanted setup, and change the devices state
    path = get_local_path("saves.txt")
    try:
        with open(path, "r", encoding="utf-8") as saveNames:
            savename = json.load(saveNames)
    except FileNotFoundError:
        logger3.error("saves.txt ei löytynyt")
        return {"error": "No saved settings found"}

    if not (0 <= index < len(savename)):
        logger3.error(f"Virheellinen indeksi: {index}")
        return {"error": "Invalid slot index"}

    selected_name = savename[index]
    logger3.info(f"Valittu asetuksen nimi: {selected_name}")

    # Ladataan tallennettu JSON-tiedosto
    json_path = get_local_path(f"{selected_name}.json")
    try:
        with open(json_path, "r", encoding="utf-8") as SavedSettingsJsonFile:
            loaded_config = json.load(SavedSettingsJsonFile)
    except FileNotFoundError:
        logger3.error(f"Tiedostoa {selected_name}.json ei löytynyt")
        return {"error": "Saved configuration not found"}

    current_devices = json.loads(wlan_devices.get_json())
    return_wlan_devices_from_phone(loaded_config, current_devices, devices)
    saveNames.close()
    SavedSettingsJsonFile.close()

    return {"status": f"Settings '{selected_name}' executed"}


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

