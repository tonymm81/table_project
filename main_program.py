from logging import root
from sre_parse import State
from tkinter import *
from broadlink import *
from save_to_file import *
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
#import smbus

#pin numbering
trigger = 7
echo = 14
relay_down_limit = 8
relay_switch_direction = 25
relay_up_limit = 23
relay_up = 15
relay_down = 12
temp_value = 0
level1 = 0
devices_library = '{}' # here we save the devices name, ipaddress, lightbulb color setup, and devices state
devices = []
json.dumps(devices_library, indent=4)
#gpio setups
GP.setwarnings(False)
GP.setmode(GP.BCM)
GP.setup(trigger, GP.OUT)
GP.setup(echo, GP.IN)
GP.setup(relay_down_limit, GP.IN)
GP.setup(relay_switch_direction, GP.OUT)
GP.setup(relay_up_limit, GP.IN)
GP.setup(relay_up, GP.OUT)
GP.setup(relay_down, GP.OUT)
GP.output(relay_switch_direction, GP.LOW)
GP.output(relay_up, GP.LOW)
GP.output(relay_down, GP.LOW)
#GP.setup(echo, GP.IN, pull_up_down=GP.PUD_DOWN)
GP.add_event_detect(relay_up_limit, GP.RISING)
GP.add_event_detect(relay_down_limit, GP.RISING)

#graphical view and buttons
root = Tk()
root.geometry("880x450")
root.configure(background="black")
#scrollbar = Scrollbar(root)
#scrollbar.pack( side = RIGHT, fill = Y )
btn = Button(root, text="Adjust table up",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_up()).pack() 
btn1 = Button(root, text="Adjust table down",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_down()).pack() 
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: search_all_devices_wlan(devices)).pack() 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_setup()).pack() 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: load_setup()).pack() 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).pack()
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).pack() 
btn6 = Button(root, text="Check the updates",fg="white", bg="black",font=("helvetica", 15), command=lambda: measure_distance()).pack() 
label_1 = Label(root, text= "sais", font=("helvetica", 25), fg="white", bg="black")
label_1.pack()
#ultrasonic_ranger = trigger
#test_json = {"testing": 123, "Riipuksen eteinen valo|-1": ["192.168.68.115", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Keitti\u00f6 Valo|9": ["192.168.68.106", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen kaffinkeiti|-1": ["192.168.68.105", false, 30073], "Riipuksen makkari valo|-1": ["192.168.68.100", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Makkari pistorasia|1": ["192.168.68.104", false, 32000], "Esp Bedroom|1": ["192.168.68.125", false, 32000], "Esp Kitchen|1": ["192.168.68.126", false, 32000], "Riipuksen Olkkari Valo|9": ["192.168.68.110", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Valo3|9": ["192.168.68.111", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Weatherstation Riipus|1": ["192.168.68.127", false, 30073], "Riipukksen Olkkari Ledi|1": ["192.168.68.119", false, 30073], "Riipuksen Olkkari Valo2|9": ["192.168.68.112", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipukse Ty\u00f6piste val|9": ["192.168.68.129", {"red": 0, "blue": 0, "green": 0, "pwr": 1, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Tv, Stereot|1": ["192.168.68.109", true, 32000], "Riipuksen Olkkari Tietsikka|1": ["192.168.68.107", true, 32000], "Riipuksen Olkkari Ty\u00f6piste|1": ["192.168.68.108", false, 32000], "Riipuksen Imari|1": ["192.168.68.123", false, 32000]}
#test_json.dumps(test_json)
button_dict = {}

def update_setpoint(level):#needed to update the level value
    global level1
    level1 = level
    print(level1)
    return

def ask_user(level, direction, limit_switch): # here user can select how far table is from floor
    level = DoubleVar()
    top1 = Toplevel()
    top1.title('table measurement')
    top1.geometry("400x300")
    top1.configure(background="white")
    top1.update()
    l2 = Label(top1)
    s2 = Scale( top1, variable = level,from_ = 50, to = 1,orient = VERTICAL)
    s2.pack(anchor = CENTER)
    
    sel = "Vertical Scale Value = " + str(level.get())
    l2.config(text = sel, font =("Courier", 14)) 
     
  
    l4 = Label(top1, text = "set measurement")
  
    b2 = Button(top1, text ="choose measurement",
            command = lambda:level.get(),
            bg = "purple", 
            fg = "white")
  
    #btn = Button(top1, text="stop", fg="white",bg="black", font=("helvetica", 15), command=lambda: [motor_up(1), top1.destroy()]).pack()
    b3 = Button(top1, text ="update measurement",
            command = lambda: [update_setpoint(level.get()),motor_control(level1, direction, limit_switch), top1.destroy()],
            bg = "purple", 
            fg = "white")
     
    l4.pack()
    b2.pack()
    b3.pack()
    l2.pack()
    root.update()
    level1 = level
    top1.mainloop()
    #top1.destroy()
    return level1

# here we make only one function where we bring three parameters. What direction, up/down limit/ measuring value. This how we can save lots lines of code
# lets build up the for loop what drives motor until limit switch says no or measurement goes to right distance. i dont have sensors so i have to use time rule now.
#delete the rules. lets make this to forloop anf there whe end loop when limit switch activated. no needed up or down rules anymore.perhaps we dont need to use interrupt pins
def motor_control(level1, direction, limit_switch):
    i = measure_distance() #measured distance
    i = round(i)
    i = int(i)
    print("in motor function")
    level_temp = level1.get()
    level_temp = round(level_temp)
    level_temp = int(level_temp)
    interrupt = time.time()
    interrupt_clk = time.time()
    if direction == 15: #up
        
        target_distance = level_temp + i
        print("target distance", target_distance)
        print(i)
        while True:
            GP.output(direction, GP.HIGH)
            i = measure_distance()
            i = round(i)
            i = int(i)
            GP.output(relay_switch_direction, GP.HIGH) #replace values            GP.output(relay_up, GP.HIGH)
            print("direction up and distance now:", i)
            if GP.event_detected(limit_switch):# 
                interrupt_clk = time.time()
                print("limit!!!")
                time.sleep(1)
                print(interrupt_clk - interrupt)
            
            #if interrupt_clk - interrupt >= 5  : # fix this not working
                #break
                #rint("je")
            
            if target_distance == i or target_distance < i:
                print("target")
                target_distance = 0
                i = 0
                level_temp = 0
                break
        
    if direction == 12:#down
        target_distance = i - level_temp 
        print("target", target_distance)
        print(i)
        while True:
            GP.output(direction, GP.HIGH)
            i = measure_distance()
            i = round(i)
            i = int(i)
            print("distance now",i)
            if GP.event_detected(limit_switch):# 
                interrupt_clk = time.time()
                print("limit!!!")
                time.sleep(1)
                print(interrupt_clk - interrupt)
            
            #if interrupt_clk - interrupt >= 5  : # fix this not working
                #print("je")
                #break
            
            if target_distance == i or target_distance > i :
                print("target")
                target_distance = 0
                i = 0
                level_temp = 0
                break
    
    if direction == 15:
        GP.output(relay_switch_direction, GP.LOW) #replace values
        
    GP.output(direction, GP.LOW)
              
    return


 
 
def going_up(): #motor controlling up direction
    global level1
    direction = 15
    limit_switch = 23
    root.update()
    level1 = ask_user(level1, direction, limit_switch)
    #motor_control(level1, direction, limit_switch)
    main_waiting_loop()
    return
 
 
def going_down(): # make a function call to control motor
    global level1
    root.update()
    direction = 12
    limit_switch = 8
    level1 = ask_user(level1, direction, limit_switch)
    #motor_control(level1, "relay_down", "relay_down_limit")
    main_waiting_loop()
    return




def search_all_devices_wlan(devices): # here we check again the devices list
    # scrollbar main frame setup
    main_frame = Frame(root)
    main_frame.pack(fill=BOTH, expand=1)
    #scrollbar canvas
    my_canvas = Canvas(main_frame)
    my_canvas.pack(side=LEFT, fill=BOTH, expand=1)
    #scrollbar settings
    scrollbar1 = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
    scrollbar1.pack(side=RIGHT, fill=Y)
    #configure the canvas
    my_canvas.configure(yscrollcommand=scrollbar1.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
    #add second framee scrollbar
    second_frame = Frame(my_canvas)
    #add that new frame to window in the canvas
    my_canvas.create_window((0,0), window=second_frame, anchor="nw")
    device_names = [] # remove if not needed
    for o in range (len(devices)): # name list for the buttons
        device_names.append(devices[o].name)
        o = o +1
    
    rounds = 0
    button_rounds = 0
    update_btn = Button(second_frame, text = "Update wlan devices list", command = lambda: check_wlan_device_status(devices) , bg = "black", fg = "white")# user can manually update the wlan list
    update_btn.pack(pady=2, padx=2)
    exit_btn = Button(second_frame, text = "EXIT", command = lambda: [second_frame.destroy(), main_frame.destroy()] , bg = "black", fg = "white")# exit button
    exit_btn.pack(pady=2, padx=2)
    devices_library_tmp = json.loads(devices_library)
    print(button_dict)
    
    for i in range (len(devices)):
        #print(devices_library_tmp[device_names[rounds]][1])
        
        if devices_library_tmp[device_names[rounds]][1] == False: # here we choose color on label based on wlan state is it on or off
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="red")
            infolabel.pack(pady=0, padx=0)
            
        elif devices_library_tmp[device_names[rounds]][2] == 24686 and devices_library_tmp[device_names[rounds]][1]['pwr'] == 0:
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="red")
            infolabel.pack(pady=0, padx=0)
            
        else:
            infolabel = Label(second_frame, text=device_names[rounds],font=("helvetica", 8), fg="black", bg="green")
            infolabel.pack(pady=2, padx=2)
         
        btn = device_names[rounds]
        dev_name_temp = device_names[rounds]# not working, saves last one only
        print("temp json" ,devices_library_tmp) 
        exec(devices_library_tmp[device_names[rounds]][3])# print clause wont work on this # gives a keyerror 'p' when key is not found in a dictoriany. json shows correct infoemation
        exec(devices_library_tmp[device_names[rounds]][4])
        #btn = device_names[rounds]
        #dev_name_temp = device_names[rounds]# not working, saves last one only 
        #btn = Button(second_frame, text = btn, command = lambda: control_wlan_devices(dev_name_temp, devices, devices_library), bg = "black", fg = "white") # make here function call
        #btn.pack(pady=2, padx=2)
        i = i +1
        rounds = rounds +1
        button_rounds = button_rounds+100
        #dev_name_temp = ""
        #break
        
    print(button_dict)
    second_frame.mainloop()
    return devices
 
 
def load_setup():
     return
 
 
def save_setup():
     return
 
 
def measure_distance():
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
 
 
def exit_and_shutdown():
    GP.cleanup()
    root.destroy()
    return
 
 
def exit_only():
    GP.cleanup()
    root.destroy()
    return
 
 
def main_waiting_loop():
    
    distance = measure_distance()
    distance = round(distance)
    distance = int(distance)
    label_1.configure(text = "waiting user to choose and distance is: " + str(distance))
    label_1.pack()
    time.sleep(1)
    
    
    #print(distance)
    return



def check_updates():
    return


def check_wlan_device_status(devices): # check here also buttons and save device in button command
    global devices_library
    temp_json = json.loads(devices_library)
    
    for i in range (len(devices)):
        #print("before if clause", devices[i].devtype)
        devtype = devices[i].devtype
        
        
        if devtype == 24686:
            bulb_button = " "
            bulb_pack = " "
            bulbname = devices[i].name  
        
            temp_str_bulb = devices[i]
            temp_str_bulb = str(temp_str_bulb)
            result_bulb = re.findall(r'[\d\.]+', temp_str_bulb)
            bulb_ip = result_bulb[5]#this works on sp3-eu plugs and [4] works with sp4-eu light bulb test it
            bulb_button = devices[i].name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices(" '{devices[i].name}'", devices, devices_library), bg = 'black', fg = 'white')"
            bulb_pack = devices[i].name+".pack(pady=2, padx=2)"
            if len(bulb_ip) < 9:
                bulb_ip = result_bulb[4]
                
            result_bulb.clear()
            print(bulb_ip, bulbname)
            devices_temp1 = broadlink.discover(timeout=5, discover_ip_address=bulb_ip)
            devices_temp1[0].auth()
            dev_name_status = bulbname 
            device_state1 = devices_temp1[0].get_state()
            bulb_library = {bulbname : [bulb_ip,  device_state1, devtype, bulb_button, bulb_pack]}#temp value to json
            temp_json.update(bulb_library)
            dev_name_status = ""
            
        if devtype == 30073:
            sp4_button = " "
            sp4_pack = " "
            sp4_name = devices[i].name
            temp_str_sp4 = devices[i]
            temp_str_sp4 = str(temp_str_sp4)
            result_sp4 = re.findall(r'[\d\.]+', temp_str_sp4)
            sp4_button = devices[i].name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices(" '{devices[i].name}'", devices, devices_library), bg = 'black', fg = 'white')"
            sp4_pack = devices[i].name+".pack(pady=2, padx=2)"
            sp4_ip = result_sp4[5]#this works on sp3-eu plugs and [4] works with sp4-eu
            if len(sp4_ip) < 9:
                sp4_ip = result_sp4[4]
                
            result_sp4.clear()
            print(sp4_ip, sp4_name)
            devices_temp2 = broadlink.discover(timeout=5, discover_ip_address=sp4_ip)
            devices_temp2[0].auth()
            device_state2 = devices_temp2[0].check_power()
            dev_name_status = sp4_name
            sp4_library = {sp4_name : [sp4_ip,  device_state2, devtype, sp4_button, sp4_pack]}#temp value to json
            temp_json.update(sp4_library)
            dev_name_status = ""
            
            
        if devtype == 32000:
            
            sp3_button = " "
            sp3_pack = " "
            sp3_name = devices[i].name
            temp_str_sp3 = devices[i]#here was problem
            temp_str_sp3 = str(temp_str_sp3)
            result_sp3 = re.findall(r'[\d\.]+', temp_str_sp3)
            sp3_ip = result_sp3[5]#this works on sp3-eu plugs and [4] works with sp4-eu
            if len(sp3_ip) < 9:
                sp3_ip = result_sp3[4]
                
            sp3_button = devices[i].name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices(" '{devices[i].name}'", devices, devices_library), bg = 'black', fg = 'white')"
            sp3_pack = devices[i].name+".pack(pady=2, padx=2)"
            print(sp3_ip, sp3_name)
            result_sp3.clear()
            devices_temp3 = broadlink.discover(timeout=5, discover_ip_address=sp3_ip)
            devices_temp3[0].auth()
            device_state3 = devices_temp3[0].check_power()
            dev_name_status = sp3_name
            sp3_library = {sp3_name : [sp3_ip, device_state3, devtype, sp3_button, sp3_pack]} #temp value to json
            temp_json.update(sp3_library)
            dev_name_status = ""
            
            
        devtype = 0
     
    
    devices_library = json.dumps(temp_json)
    print(devices_library)
    pprint.pprint(devices_library) # easier way to read json value
    return devices


def control_wlan_devices(device_names, devices, devices_library):# here we change the wlan devices state
    device_name_tmp = device_names
    temp_json = json.loads(devices_library)
    print(device_name_tmp)
    print(temp_json[device_name_tmp][2])
    if temp_json[device_name_tmp][2] == 24686:
        print("Bulp!!!!")
    
    else:
        print("plug!!")
    
    device_name_tmp=""
    return

second_frame = "root"
devices = broadlink.discover(timeout=5, local_ip_address='192.168.68.118')# lets check devices list
check_wlan_device_status(devices) # lets check devices begin of program and convert them to json value
while True:
#    root.update()
#
    main_waiting_loop()
    root.update()
##    time.sleep(1)
#main_waiting_loop() # not helping scroll problem
#root.mainloop()