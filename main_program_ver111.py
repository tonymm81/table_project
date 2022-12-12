from inspect import Traceback
from logging import root
from sre_parse import State
from tkinter import *
import traceback
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
from subprocess import call
import socket
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
btn = Button(root, text="Adjust table up",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_up()).grid(row = 1, column=1) # replace this to grid command
btn1 = Button(root, text="Adjust table down",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_down()).grid(row=3, column=1) 
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: search_all_devices_wlan(devices)).grid(row=5, column =1) 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_setup()).grid(row=7, column=1) 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: load_setup()).grid(row=9, column =1) 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).grid(row=11, column=1)
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).grid(row=13, column=1) 
btn6 = Button(root, text="Check the updates weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: measure_distance()).grid(row=15, column=1) 
label_1 = Label(root, text= "sais", font=("helvetica", 10), fg="white", bg="black")
label_1.grid(row=17, column=1)
#test_json = {"testing": 123, "Riipuksen eteinen valo|-1": ["192.168.68.115", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Keitti\u00f6 Valo|9": ["192.168.68.106", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen kaffinkeiti|-1": ["192.168.68.105", false, 30073], "Riipuksen makkari valo|-1": ["192.168.68.100", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Makkari pistorasia|1": ["192.168.68.104", false, 32000], "Esp Bedroom|1": ["192.168.68.125", false, 32000], "Esp Kitchen|1": ["192.168.68.126", false, 32000], "Riipuksen Olkkari Valo|9": ["192.168.68.110", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Valo3|9": ["192.168.68.111", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Weatherstation Riipus|1": ["192.168.68.127", false, 30073], "Riipukksen Olkkari Ledi|1": ["192.168.68.119", false, 30073], "Riipuksen Olkkari Valo2|9": ["192.168.68.112", {"red": 0, "blue": 0, "green": 0, "pwr": 0, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipukse Ty\u00f6piste val|9": ["192.168.68.129", {"red": 0, "blue": 0, "green": 0, "pwr": 1, "brightness": 40, "colortemp": 3500, "hue": 0, "saturation": 0, "transitionduration": 1000, "maxworktime": 0, "bulb_colormode": 1, "bulb_scenes": "", "bulb_scene": ""}, 24686], "Riipuksen Olkkari Tv, Stereot|1": ["192.168.68.109", true, 32000], "Riipuksen Olkkari Tietsikka|1": ["192.168.68.107", true, 32000], "Riipuksen Olkkari Ty\u00f6piste|1": ["192.168.68.108", false, 32000], "Riipuksen Imari|1": ["192.168.68.123", false, 32000]}
#test_json.dumps(test_json)


def update_setpoint(level):#needed to update the level value
    global level1
    level1 = level
    print(level1)
    return
 
def ask_user(level, direction, limit_switch): # here user can select how far table is from floor
    level = DoubleVar()
    top1 = Toplevel()
    max_distance = 0
    
    distance_now = measure_distance() # 15 up and 12 down
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
  
    #btn = Button(top1, text="stop", fg="white",bg="black", font=("helvetica", 15), command=lambda: [motor_up(1), top1.destroy()]).pack()
    b3 = Button(top1, text ="update measurement",
            command = lambda: [update_setpoint(level.get()),motor_control(level1, direction, limit_switch), top1.destroy()],
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
            if target_distance == 111 or target_distance > 111: # max table high
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
            if target_distance == 65 or target_distance < 65:
                break
            
    
    if direction == 15:
        GP.output(relay_switch_direction, GP.LOW) #replace values
        
    GP.output(direction, GP.LOW)
              
    return


 
 
def going_up(): #motor controlling up direction max high 111
    global level1, label_1
    direction = 15
    limit_switch = 23
    root.update()
    level1 = ask_user(level1, direction, limit_switch)
    label_1.configure(text = "waiting user to choose and distance is: " + str(measure_distance()))
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
    label_1.configure(text = "waiting user to choose and distance is: " + str(measure_distance()))
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
    main_frame = Frame(top3)
    main_frame.grid(ipadx=500, ipady=800)#pack(fill=BOTH, expand=1)grid(row=1, column=1,columnspan=3,sticky='nwse')
    #scrollbar canvas
    my_canvas = Canvas(main_frame)
    my_canvas.grid(ipadx=500, ipady=800)#pack(side=LEFT, fill=BOTH, expand=1)grid(row=1, column=1,columnspan=3,sticky='nswe')
    #scrollbar settings
    scrollbar1 = ttk.Scrollbar(main_frame, orient=HORIZONTAL, command=my_canvas.yview)#set was VERTICAL
    scrollbar1.grid( column=10, ipady=700, ipadx=20)#pack(side=RIGHT, fill=Y)
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
    update_btn = Button(second_frame, text = "Update wlan devices list", command = lambda: check_wlan_device_status(devices) , bg = "black", fg = "white")# user can manually update the wlan list
    update_btn.grid(row=2, column=2)#pack(pady=2, padx=2)
    exit_btn = Button(second_frame, text = "EXIT", command = lambda: [second_frame.destroy(), main_frame.destroy(), top3.destroy()] , bg = "black", fg = "white")# exit button
    exit_btn.grid(row=7, column=2)#pack(pady=2, padx=2)
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
        
    devices_directory = json.dumps(devices_library_tmp, indent=4)
    devices_library_tmp = '{}'
    second_frame.mainloop()
    top3.mainloop()
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
    call("sudo shutdown -h now", shell=True)
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
    label_1.grid(row=17, column=1)
    time.sleep(1)
    
    
    #print(distance)
    return



def check_updates():
    return


def check_wlan_device_status(devices): # check here also buttons and save device in button command
    global devices_library # make here try exceptclause for Traceback error
    temp_json = json.loads(devices_library)
    buttons_row = 15
    for i in range (len(devices)):
        #print("before if clause", devices[i].devtype)
        devtype = devices[i].devtype
        
        
        if devtype == 24686:
            bulb_button = " "
            bulb_pack = " "
            
            bulbname = devices[i].name
            size = len(bulbname)
            temp_name = bulbname[:size -3]#delete 3 letters
            temp_str_bulb = devices[i]
            temp_str_bulb = str(temp_str_bulb)
            result_bulb = re.findall(r'[\d\.]+', temp_str_bulb)
            bulb_ip = result_bulb[5]#this works on sp3-eu plugs and [4] works with sp4-eu light bulb test it
            bulb_button = temp_name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
            bulb_pack = temp_name+ ".grid(row ="+str(buttons_row)+", column=2)" 
            if len(bulb_ip) < 9:
                bulb_ip = result_bulb[4]
                
            result_bulb.clear()
            print(bulb_ip, bulbname)
            try:
                devices_temp1 = broadlink.discover(timeout=5, discover_ip_address=bulb_ip)
                devices_temp1[0].auth()
                device_state1 = devices_temp1[0].get_state()
                 
            except traceback:
                print("device communication failed")
                
            except IndexError:
                print("device wont find")
                
            bulb_library = {bulbname : [bulb_ip,  device_state1, devtype, bulb_button, bulb_pack]}#temp value to json
            temp_json.update(bulb_library)
            
            
        if devtype == 30073:
            sp4_button = " "
            sp4_pack = " "
            sp4_name = devices[i].name
            size = len(sp4_name)
            sp4_temp_name = sp4_name[:size-3]
            temp_str_sp4 = devices[i]
            temp_str_sp4 = str(temp_str_sp4)
            result_sp4 = re.findall(r'[\d\.]+', temp_str_sp4)
            sp4_button = sp4_temp_name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
            sp4_pack = sp4_temp_name+".grid(row ="+str(buttons_row)+", column=2)"
            sp4_ip = result_sp4[5]#this works on sp3-eu plugs and [4] works with sp4-eu
            if len(sp4_ip) < 9:
                sp4_ip = result_sp4[4]
                
            result_sp4.clear()
            print(sp4_ip, sp4_name)
            try:
                devices_temp2 = broadlink.discover(timeout=5, discover_ip_address=sp4_ip)
                devices_temp2[0].auth()
                device_state2 = devices_temp2[0].check_power()
            except traceback:
                print("device communication failed")
                
            except IndexError:
                print("device wont find")
            
            
            sp4_library = {sp4_name : [sp4_ip,  device_state2, devtype, sp4_button, sp4_pack]}#temp value to json
            temp_json.update(sp4_library)
            
            
            
        if devtype == 32000:
            
            sp3_button = " "
            sp3_pack = " "
            sp3_name = devices[i].name
            size = len(sp3_name)
            sp3_temp_name = sp3_name[:size -3]
            temp_str_sp3 = devices[i]#here was problem
            temp_str_sp3 = str(temp_str_sp3)
            result_sp3 = re.findall(r'[\d\.]+', temp_str_sp3)
            sp3_ip = result_sp3[5]#this works on sp3-eu plugs and [4] works with sp4-eu
            if len(sp3_ip) < 9:
                sp3_ip = result_sp3[4]
                
            sp3_button = sp3_temp_name +" = Button(second_frame, text = btn, command = lambda: control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
            sp3_pack = sp3_temp_name +".grid(row ="+str(buttons_row)+", column=2)"
            print(sp3_ip, sp3_name)
            result_sp3.clear()
            try:
                devices_temp3 = broadlink.discover(timeout=5, discover_ip_address=sp3_ip)
                devices_temp3[0].auth()
                #print(devices[0])
                device_state3 = devices_temp3[0].check_power()

            except traceback: #TypeError: catching classes that do not inherit from BaseException is not allowed
                print("device communication failed")
                
            except IndexError:
                print("device wont find")
            
            sp3_library = {sp3_name : [sp3_ip, device_state3, devtype, sp3_button, sp3_pack]} #temp value to json
            temp_json.update(sp3_library)
            
            
            
        devtype = 0
        buttons_row = buttons_row + 3
     
    
    devices_library = json.dumps(temp_json)
    #print(devices_library)
    pprint.pprint(devices_library) # easier way to read json value
    return devices


def control_wlan_devices(device_names, devices):# here we change the wlan devices state   
    global devices_library 
    device_name_tmp = device_names
    temp_json = json.loads(devices_library)
    choice= ""   
    control = ""
    #print(device_name_tmp)
    #print(temp_json[device_name_tmp][2])
    if temp_json[device_name_tmp][2] == 24686:
        print("Bulp!!!!")
        level_red = DoubleVar()
        level_green = DoubleVar()
        level_blue = DoubleVar()
        level_bright = DoubleVar()
        level_colortmp = DoubleVar()
        level_satu = DoubleVar()
        colors = 0
        top2 = Toplevel()
        top2.title('light adjusment')
        top2.geometry("400x300")
        top2.configure(background="white")
        top2.update()
        
        
        s2 = Scale( top2, variable = level_red,from_ = 255, to = 1,orient = VERTICAL) #red
        s2.grid(row=2, column=2)#s2.pack(anchor = RIGHT)
        s3 = Scale( top2, variable = level_green,from_ = 255, to = 1,orient = VERTICAL) #green
        s3.grid(row=2, column=5)#pack(anchor = RIGHT)
        s4 = Scale( top2, variable = level_blue,from_ = 255, to = 1,orient = VERTICAL) #blue
        s4.grid(row=2, column=7)#pack(anchor = CENTER)
        s5 = Scale( top2, variable = level_bright,from_ = 255, to = 1,orient = VERTICAL) #brightness
        s5.grid(row=2, column=9)#.pack(anchor = CENTER)
        s6 = Scale( top2, variable = level_colortmp,from_ = 5, to = 0,orient = VERTICAL) # clolortemp 
        s6.grid(row=2, column=11)#.pack(anchor = LEFT)
        red = Button(top2, text="red", fg="white",bg="black", font=("helvetica", 6), command=lambda: set_state_bulp(temp_json, device_name_tmp, control, "red", s2.get()) )
        green = Button(top2, text="green", fg="white",bg="black", font=("helvetica", 6), command=lambda: set_state_bulp(temp_json, device_name_tmp, control, "green", s3.get()) )
        blue = Button(top2, text="blue", fg="white",bg="black", font=("helvetica", 6), command=lambda: set_state_bulp(temp_json, device_name_tmp, control, "blue", s4.get()) )
        bright = Button(top2, text="brightn.", fg="white",bg="black", font=("helvetica", 6), command=lambda: set_state_bulp(temp_json, device_name_tmp, control, "bright", s5.get()) )
        colortemp = Button(top2, text="colortmp", fg="white",bg="black", font=("helvetica", 6), command=lambda: set_state_bulp(temp_json, device_name_tmp, control, "colortmp", s6.get()) )
    
        for i in range(len(devices)):
            if device_name_tmp == devices[i].name:
                control = devices[i]
                #print(control)
                break
        btn = Button(top2, text="exit", fg="white",bg="black", font=("helvetica", 15), command=lambda: top2.destroy() )
        b3 = Button(top2, text ="on / off",
            command = lambda: set_state_bulp(temp_json, device_name_tmp, control, "pwr", 0),
            bg = "purple", 
            fg = "white")
        btn.grid(row=26, column = 3)
        b3.grid(row=24, column=3)
        red.grid(row=20, column=2)
        green.grid(row=20, column =5)
        blue.grid(row=20, column= 7)
        bright.grid(row=20, column=9)
        colortemp.grid(row=20, column=11)
        root.update()
        top2.mainloop()
    else:
       
        print("plug!!")
        for i in range(len(devices)):
            if device_name_tmp == devices[i].name:
                control = devices[i]
                break
            
        control.auth()
        switch_state = control.check_power()
        
        if switch_state == True:
            control.set_power(False)
            
        elif switch_state == False:
            control.set_power(True)
            
    switch_state = control.check_power()
    temp_json[device_name_tmp][1] = switch_state
    devices_library = json.dumps(temp_json, indent=4)
    #device_name_tmp=""
    return 


def set_state_bulp(temp_json,device_name_tmp, control, colors, choice):
    value_number = choice
    value_number = int(value_number)
    colors_ = str(colors)
    global devices_library
    print("colors", str(colors))
    #state_=2
    control.auth()
    state = control.get_state()
    if colors_ == "pwr":
        if state['pwr'] == 0:
            control.set_state(pwr=1)
            state_ = 1
        
        else:
            control.set_state(pwr=0)
            state_ = 0
    elif colors_ == "red":
        control.set_state(red=value_number)
        
    elif colors_ == "green":
        control.set_state(green=value_number)
        
    elif colors_ == "blue":
        control.set_state(blue=value_number)
        
    elif colors_ == "bright":
        control.set_state(brightness=value_number)
        
    elif colors_ == "colortmp":
        control.set_state(bulb_colormode=value_number)
    
    state = control.get_state()
    temp_json[device_name_tmp][1]['pwr'] = state['pwr']
    #print("whole json" ,temp_json[device_name_tmp])
    #print("testing", device_name_tmp, "json", str(temp_json[device_name_tmp][1]['pwr']))
    devices_library = json.dumps(temp_json, indent=4)
    
     
    return 

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname) # lets check the devies ip address

devices = broadlink.discover(timeout=5, local_ip_address=IPAddr)# lets check devices list '192.168.68.118'
check_wlan_device_status(devices) # lets check devices begin of program and convert them to json value
while True:
#    root.update()
#
    main_waiting_loop()
    root.update()
##    time.sleep(1)
#main_waiting_loop() # not helping scroll problem
#root.mainloop()
    