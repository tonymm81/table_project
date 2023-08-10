from tkinter import *
import json
import wlan_devices
import motorcontrol
import time

savenumber = 0
savename = ["save1", "save2", "save3", "save4"] # this we will save to file. This how we know what name of json file we are looking for..

def starting():
    top4 = Toplevel()
    top4.title("Save or load settings")
    top4.geometry("800x500")
    top4.configure(background="black")
    exit_btn = Button(top4, text="Exit",fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 22, column=1)
    return top4


def load_settings(echo, trigger, devices):
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


def save_settings(echo, trigger):
    top4 = starting()
    measure = motorcontrol.measure_table(echo, trigger)
    listbox = Listbox(top4, width=40, height=10, selectmode=SINGLE)
    listbox.grid(row=15, column=1)
    listbox.insert(1, 0)
    listbox.insert(2, 1)
    listbox.insert(3, 2)
    listbox.insert(4, 3)
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
    measure_from_floor = "distance from floor"
    save_json = wlan_devices.get_json()
    save_json_temp = json.loads(save_json)
    for i in listbox.curselection():
        saveslot = listbox.get(i) # we can try .index(i)
        
        
    name_file= entry.get()
    print("test", name_file, saveslot)
    savename[saveslot] = str(name_file)
    desk_level = {measure_from_floor : [measure] }
    save_json_temp.update(desk_level)
    save_json= json.dumps(save_json_temp, indent=4)
    with open(f"{name_file}.json", "w") as outfile: #lets save user setup to file what user has giveb the name
        outfile.write(save_json)
        #json.dump(save_json, outfile)
        
    file = open('saves.txt','w')
    for item in savename: # lets save the user modified list to file
	    file.write(item + "\n")
     
     
    file.close()
    return

def return_wlan_devices(saveslot, echo, trigger, devices): # here we open new and saved json and measure table distance from loaded json value
    new_json = wlan_devices.get_json() # this is new. based on start time
    new_json_temp = json.loads(new_json)
    size = len(saveslot)
    saveslot_temp = saveslot[:size -1]#lets delete newline
    
    with open(f'{saveslot_temp}.json') as json_file:
        saved_json = json.load(json_file)
        #saved_json = json.loads(saved_jsontemp)
        
    print("loaded json", saved_json)
    json_file.close()
    #temp_json = saved_json
    #saved_json = json.loads(temp_json)
    # here we check if the table is lower or higer in saved settings comparing new json value
    #if saved_json["distance from floor"] < new_json_temp["distance from floor"]: # lets adjust table up
        #motorcontrol.motor_control(saved_json["distance from floor"], 15, 23, echo, trigger)
       # print("motor up", saved_json["distance from floor"], new_json_temp["distance from floor"])
    
   # if saved_json["distance from floor"] > new_json_temp["distance from floor"]:# lets adjust table down
        #motorcontrol.motor_control(saved_json["distance from floor"], 12, 8, echo, trigger)
      #  print("motor up", saved_json["distance from floor"], new_json_temp["distance from floor"])
        
    # here we will check the wlan devices state and turn on or off comparing saved settings
    for i in range (len(saved_json)):
        device_saved = saved_json[i] # lets save first device name
        
        for x in range (len(new_json_temp)): # lets compare if found on json
            if device_saved[0] == new_json_temp[x]:
                print("same device")
                if saved_json[device_saved[0]][1] != new_json_temp[x][1]: # if state is different lets start of shutdown the device
                    #wlan_devices.control_wlan_devices(device_saved[0], devices)
                    print("change plug state", aved_json[device_saved[0]][1], new_json_temp[x][1])
                if saved_json[device_saved[0]][1]['pwr'] != new_json_temp[x][1]['pwr']:
                    #wlan_devices.set_state_bulp(new_json_temp, device_saved[0], "", "pwr", 0)    
                    print("change bulp state", saved_json[device_saved[0]][1]['pwr'], new_json_temp[x][1]['pwr'])
                    
            x = x +1
            print("inner loop", x, device_saved[0])
                    
        i = i+1
        print("outer loop", i, device_saved[0])
    return

