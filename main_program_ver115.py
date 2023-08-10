from inspect import Traceback
from logging import root
from sre_parse import State
from tkinter import *
import traceback
from broadlink import *
from shutdown_weatherstation import *
import broadlink # wlan plus bulps
from tkinter import ttk # scrollbar ver106
import RPi.GPIO as GP
import sys
import time
import os
import re
import json
import pprint
from subprocess import call
import wlan_devices
import socket
import save_to_file
import motorcontrol
#import smbus

#pin numbering
trigger = 7
echo = 14

temp_value = 0
level1 = 0

#gpio setups
GP.setwarnings(False)
GP.setmode(GP.BCM)
GP.setup(trigger, GP.OUT)
GP.setup(echo, GP.IN)


#graphical view and buttons
root = Tk()
root.geometry("880x450")
root.configure(background="black")
btn = Button(root, text="Adjust table up",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_up()).grid(row = 1, column=1) # replace this to grid command
btn1 = Button(root, text="Adjust table down",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_down()).grid(row=3, column=1) 
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: search_all_devices_wlan(devices)).grid(row=5, column =1) 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_to_file.save_settings(echo, trigger)).grid(row=7, column=1) 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_to_file.load_settings(echo, trigger, devices)).grid(row=9, column =1) 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).grid(row=11, column=1)
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).grid(row=13, column=1) 
btn6 = Button(root, text="Check the updates weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: motorcontrol.measure_table()).grid(row=15, column=1) 
label_1 = Label(root, text= "sais", font=("helvetica", 10), fg="white", bg="black")
label_1.grid(row=17, column=1)
#test_json = {"testing": 123, "Riipuksen eteinen valo|-1": ["192.168.68.115", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Keitti\u00f6 Valo|9": ["192.168.68.106", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen kaffinkeiti|-1": ["192.168.68.105", false, 30073], "Riipuksen makkari valo|-1": ["192.168.68.100", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Makkari pistorasia|1": ["192.168.68.104", false, 32000], "Esp Bedroom|1": ["192.168.68.125", false, 32000], "Esp Kitchen|1": ["192.168.68.126", false, 32000], "Riipuksen Olkkari Valo|9": ["192.168.68.110", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Valo3|9": ["192.168.68.111", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Weatherstation Riipus|1": ["192.168.68.127", false, 30073], "Riipukksen Olkkari Ledi|1": ["192.168.68.119", false, 30073], "Riipuksen Olkkari Valo2|9": ["192.168.68.112", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipukse Ty\u00f6piste val|9": ["192.168.68.129", {"red": 0, "blue": 0, "green": 0, "pwr": 1, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Tv, Stereot|1": ["192.168.68.109", true, 32000], "Riipuksen Olkkari Tietsikka|1": ["192.168.68.107", true, 32000], "Riipuksen Olkkari Ty\u00f6piste|1": ["192.168.68.108", false, 32000], "Riipuksen Imari|1": ["192.168.68.123", false, 32000]}
#test_json.dumps(test_json)



 
def ask_user(level, direction, limit_switch): # here user can select how far table is from floor
    level = DoubleVar()
    top1 = Toplevel()
    max_distance = 0
    
    distance_now = motorcontrol.measure_table(echo, trigger) # 15 up and 12 down
    if direction == 12: #down
        max_distance = distance_now - 65 
        
    if direction == 15:
        max_distance = 111 - distance_now 
    
    top1.title('table measurement')
    top1.geometry("400x300")
    top1.configure(background="white")
    top1.update()
    l2 = Label(top1)
    s2 = Scale( top1, variable = level,from_ = max_distance, to = 1,orient = VERTICAL)
    s2.grid(row=10, column=10)
    sel = "Vertical Scale Value = " + str(level.get())
    l2.config(text = sel, font =("Courier", 14)) 
    l4 = Label(top1, text = "set measurement")
    b2 = Button(top1, text ="choose measurement",
            command = lambda:level.get(),
            bg = "purple", 
            fg = "white")
  
    b3 = Button(top1, text ="update measurement",
            command = lambda: [motorcontrol.update_setpoint(level.get()),motorcontrol.motor_control(level1, direction, limit_switch, echo, trigger), top1.destroy()],
            bg = "purple", 
            fg = "white")
     
    l4.grid(row=15, column=10)
    b2.grid(row=17, column=10)
    b3.grid(row=19, column=10)
    l2.grid(row=25, column=10)
    root.update()
    level1 = level
    top1.mainloop()
    #top1.destroy()
    return level1



def going_up(): #motor controlling up direction max high 111
    global level1, label_1
    direction = 15
    limit_switch = 23
    root.update()
    level1 = ask_user(level1, direction, limit_switch)
    label_1.configure(text = "waiting user to choose and distance is: " + str(motorcontrol.measure_table(echo, trigger)))
    label_1.grid(row=17, column=1)
    main_waiting_loop()
    return
 
 
def going_down(): # make a function call to control motor min high 65
    global level1, label_1
    root.update()
    direction = 12
    limit_switch = 8
    level1 = ask_user(level1, direction, limit_switch)
    #motor_control(level1, "relay_down", "relay_down_limit")
    label_1.configure(text = "waiting user to choose and distance is: " + str(motorcontrol.measure_table(echo, trigger)))
    label_1.grid(row=17, column=1)
    main_waiting_loop()
    return


def search_all_devices_wlan(devices): # here we check again the devices list
    # scrollbar main frame setup
    top3 = Toplevel()
    top3.title('wlan devices')
    top3.geometry("800x500")
    top3.configure(background="white")
    top3.update()
    main_frame = Frame(top3, bg="black")
    main_frame.grid(sticky='news')#pack(fill=BOTH, expand=1)grid(row=1, column=1,columnspan=3,sticky='nwse')
    #scrollbar canvas
    my_canvas = Canvas(main_frame, bg='gray')
    my_canvas.grid(row=0, column=0, sticky='nw')#pack(side=LEFT, fill=BOTH, expand=1)grid(row=1, column=1,columnspan=3,sticky='nswe')
    #scrollbar settings
    scrollbar1 = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)#set was VERTICAL
    scrollbar1.grid(row=0, column=1, sticky='ns' )#pack(side=RIGHT, fill=Y)
    #configure the canvas
    my_canvas.configure(yscrollcommand=scrollbar1.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
    #add second framee scrollbar
    second_frame = Frame(my_canvas)
    #add that new frame to window in the canvas
    my_canvas.create_window((0,0), window=second_frame, anchor="ne")
    device_names = [] # remove if not needed
    for o in range (len(devices)): # name list for the buttons
        device_names.append(devices[o].name)
        o = o +1
    
    
    rounds = 0
    button_rounds = 15
    update_btn = Button(second_frame ,text = "Update wlan devices list", command = lambda: wlan_devices.check_wlan_device_status(devices) , bg = "black", fg = "white")# user can manually update the wlan list
    update_btn.grid(row=2, column=2)#pack(pady=2, padx=2)
    exit_btn = Button(second_frame , text = "EXIT", command = lambda: [second_frame.destroy(), main_frame.destroy(), top3.destroy()] , bg = "black", fg = "white")# exit button
    exit_btn.grid(row=7, column=2)#pack(pady=2, padx=2)
    devices_library = wlan_devices.get_json()
    devices_library_tmp = json.loads(devices_library)
    #print(button_dict)
    
    for i in range (len(devices)):
        #print(devices_library_tmp[device_names[rounds]][1])
        
        if devices_library_tmp[device_names[rounds]][1] == False: # here we choose color on label based on wlan state is it on or off
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="red")
            infolabel.grid(row=button_rounds, column=7)#pack(pady=0, padx=0)
            
        elif devices_library_tmp[device_names[rounds]][2] == 24686 and devices_library_tmp[device_names[rounds]][1]['pwr'] == 0:
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="red")
            infolabel.grid(row=button_rounds, column=7)#pack(pady=0, padx=0)
            
        else:
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="green")
            infolabel.grid(row=button_rounds, column=7)#pack(pady=2, padx=2)
         
        btn = device_names[rounds]
        dev_name_temp = device_names[rounds]# not working, saves last one only
        #print("temp json" ,devices_library_tmp) 
        exec(devices_library_tmp[device_names[rounds]][3])# this runs code fromjson library. this defines the buttons based on wlan devices.
        exec(devices_library_tmp[device_names[rounds]][4])
        i = i +1
        rounds = rounds +1
        button_rounds = button_rounds+3
        #dev_name_temp = ""
        #break
        
    devices_directory = json.dumps(devices_library_tmp, indent=4) # check if needed?
    devices_library_tmp = '{}'
    second_frame.mainloop()
    top3.mainloop()
    return devices
 
  
def exit_and_shutdown():
    GP.cleanup()
    root.destroy()
    call("sudo shutdown -h now", shell=True)
    return
 
 
def exit_only():
    GP.cleanup()
    root.destroy()
    return
 
 
def main_waiting_loop():
    
    distance = motorcontrol.measure_table(echo, trigger)
    label_1.configure(text = "waiting user to choose and distance is: " + str(distance))
    label_1.grid(row=17, column=1)
    time.sleep(1)
    return


def check_updates():
    return


ipv4 = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip() # this how we take broker ip address in beging of program-
devices = broadlink.discover(timeout=5, local_ip_address=ipv4)# lets check devices list '192.168.68.118'
devices_library_main = wlan_devices.check_wlan_device_status(devices) # lets check devices begin of program and convert them to json value
while True:
#    root.update()
#
    main_waiting_loop()
    root.update()
##    time.sleep(1)
#main_waiting_loop() # not helping scroll problem
#root.mainloop()
    