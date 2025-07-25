from tkinter import *
import json
import wlan_devices
import motorcontrol
import time
from tkinter import ttk

savenumber = 0
savename = ["save1", "save2", "save3", "save4"] # this we will save to file. This how we know what name of json file we are looking for..

def starting():
    top4 = Toplevel()
    top4.title("Save or load settings")
    top4.geometry("800x500")
    top4.configure(background="black")
    exit_btn = Button(top4, text="Exit",fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 22, column=1)
    return top4


def load_settings(devices):
    global savename
    
    with open('saves.txt', 'r') as file:
        # Read all the lines of the file into a list
        lines = file.readlines()
        
    savename = lines
    print("testing list", savename)
    file.close()
    
    top4 = starting()
    label_1 = Label(top4, text= "Choose what setup we load?", font=("helvetica", 10), fg="white", bg="black")
    label_1.grid(row=1, column=1)
    load_json = wlan_devices.get_json()
    load_btn1 = Button(top4, text=str(savename[0]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[0], echo, trigger, devices)).grid(row = 3, column=1)
    load_btn2 = Button(top4, text=str(savename[1]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[1], echo, trigger, devices)).grid(row = 5, column=1)
    load_btn3 = Button(top4, text=str(savename[2]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[2], echo, trigger, devices)).grid(row = 7, column=1)
    load_btn4 = Button(top4, text=str(savename[3]),fg="white", bg="black",font=("helvetica", 15), command=lambda: return_wlan_devices(savename[3], echo, trigger, devices)).grid(row = 9, column=1)
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

def get_user_data(listbox, entry, measure):
    global savename
    measure_from_floor = "distance_from_floor"
    save_json = wlan_devices.get_json()
    save_json_temp = json.loads(save_json)  # Muunna JSON-merkkijono Python-sanakirjaksi
    for i in listbox.curselection():
        saveslot = listbox.index(i)
        
    name_file = entry.get()
    print("test", name_file, saveslot)
    savename[saveslot] = str(name_file)
    desk_level = {measure_from_floor: [measure]}
    save_json_temp.update(desk_level)
    wlan_devices.update_json(save_json_temp)
    
    with open(f"{name_file}.json", "w", encoding="utf-8") as outfile:
        json.dump(save_json_temp, outfile, ensure_ascii=False)  # Tallenna JSON-tiedosto
        
    with open('saves.txt', 'w') as file:
        for item in savename:
            file.write(item + "\n")
     
    return

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
            motorcontrol.motor_control(level,  15, 23, echo, trigger)
            print("motor up", saved_json["distance_from_floor"][0], new_json_temp["distance_from_floor"][0], max_distance)            
            rootloading.update()
            progressbar.update()


        if float(saved_json["distance_from_floor"][0]) < float(new_json_temp["distance_from_floor"][0]):# lets adjust table down
            max_distance = new_json_temp["distance_from_floor"][0] - saved_json["distance_from_floor"][0] 
            level.set(max_distance)
            motorcontrol.motor_control( level, 12, 8, echo, trigger)
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
    progressbar.stop()
    rootloading.destroy()
    progressbar.destroy()       
    return

