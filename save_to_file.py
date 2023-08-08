from tkinter import *
import json
import wlan_devices
import RPi.GPIO as GP
import time

savenumber = 0
savename = ["save1", "save2", "save3", "save4"]

def measure_table(echo, trigger):
    GP.output(trigger, True)
    time.sleep(0.00001)
    GP.output(trigger, False)
    StartTime = time.time()
    StopTime = time.time()
    while GP.input(echo) == 0:
        StartTime = time.time()
        
        
    while GP.input(echo) == 1:
        StopTime = time.time()
    
    time.sleep(0.4)
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance


def starting():
    top4 = Toplevel()
    top4.title("Save or load settings")
    top4.geometry("800x500")
    top4.configure(background="black")
    exit_btn = Button(top4, text="Exit",fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy()).grid(row = 22, column=1)
    return top4


def load_settings(echo, trigger):
    global savename
    top4 = starting()
    label_1 = Label(top4, text= "Choose what setup we load?", font=("helvetica", 10), fg="white", bg="black")
    label_1.grid(row=1, column=1)
    load_json = wlan_devices.get_json()
    load_btn1 = Button(top4, text=str(savename[0]),fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy).grid(row = 3, column=1)
    load_btn2 = Button(top4, text=str(savename[1]),fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy).grid(row = 5, column=1)
    load_btn3 = Button(top4, text=str(savename[2]),fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy).grid(row = 7, column=1)
    load_btn4 = Button(top4, text=str(savename[3]),fg="white", bg="black",font=("helvetica", 15), command=lambda: top4.destroy).grid(row = 9, column=1)
    top4.update()
    return


def save_settings(echo, trigger):
    top4 = starting()
    measure = measure_table(echo, trigger)
    listbox = Listbox(top4, width=40, height=10, selectmode=MULTIPLE)
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
    top4.update()
    return

def get_user_data(listbox, entry, measure):
    global savename
    measure_from_floor = "distance from floor"
    save_json = wlan_devices.get_json()
    save_json_temp = json.loads(save_json)
    for i in listbox.curselection():
        saveslot = listbox.get(i)
        
        
    name_file= entry.get()
    print("test", name_file, saveslot)
    savename[saveslot] = str(name_file)
    desk_level = {measure_from_floor : measure }
    save_json_temp.update(desk_level)
    save_json= json.dumps(save_json_temp, indent=4)
    with open(f"{name_file}.json", "w") as outfile: #lets save user setup to file what user has giveb the name
        outfile.write(save_json)
        
        
    file = open('items.txt','w')
    for item in savename: # lets save the user modified list to file
	    file.write(item+"\n")
     
     
    file.close()
    return

def return_wlan_devices():
    return

