from logging import root
from tkinter import *
from broadlink import *
from save_to_file import *
from shutdown_weatherstation import *
import broadlink # wlan plus bulps

import RPi.GPIO as GP
import sys
import time
import os
#import smbus

trigger = 7
echo = 14
relay_down_limit = 8
relay_switch_direction = 25
relay_up_limit = 23
relay_up = 15
relay_down = 12
up_rule = 0
down_rule = 0
temp_value = 0
level1 = 0
what_device = ""

GP.setwarnings(False)
GP.setmode(GP.BCM)
GP.setup(trigger, GP.IN)
GP.setup(echo, GP.IN)
GP.setup(relay_down_limit, GP.IN)
GP.setup(relay_switch_direction, GP.OUT)
GP.setup(relay_up_limit, GP.IN)
GP.setup(relay_up, GP.OUT)
GP.setup(relay_down, GP.OUT)
GP.output(relay_switch_direction, GP.LOW)
GP.output(relay_up, GP.LOW)
GP.output(relay_down, GP.LOW)
GP.setup(trigger, GP.IN, pull_up_down=GP.PUD_DOWN)
#GP.setup(relay_down_limit, GP.IN, pull_up_down=GP.PUD_DOWN)
#GP.setup(relay_up_limit, GP.IN, pull_up_down=GP.PUD_DOWN)

root = Tk()
root.geometry("880x500")
root.configure(background="black")
scrollbar = Scrollbar(root)
scrollbar.pack( side = RIGHT, fill = Y )
btn = Button(root, text="Adjust table up",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_up(level1)).pack() 
btn1 = Button(root, text="Adjust table down",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_down(level1)).pack() 
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: control_wlan_devices()).pack() 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_setup()).pack() 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: load_setup()).pack() 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).pack()
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).pack() 
btn6 = Button(root, text="Check the updates",fg="white", bg="black",font=("helvetica", 15), command=lambda: measure_distance()).pack() 
label_1 = Label(root, text= "sais", font=("helvetica", 25), fg="white", bg="black")
label_1.pack()
#ultrasonic_ranger = trigger
GP.add_event_detect(relay_up_limit, GP.RISING)
GP.add_event_detect(relay_down_limit, GP.RISING)

def update_setpoint(level):
    global level1
    level1 = level
    print(level1)
    return

def ask_user(level, what_device):
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
  
    btn = Button(top1, text="stop", fg="white",bg="black", font=("helvetica", 15), command=lambda: [motor_up(1), top1.destroy()]).pack()
    b3 = Button(top1, text ="update measurement",
            command = lambda: [update_setpoint(level.get()), motor_up(0)],
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


def motor_up(up_rule):
    global level1
    print("in motorfunction")
    if up_rule == 1:
        print("ei mennä ylös")
        GP.output(relay_up, GP.LOW)
        GP.output(relay_switch_direction, GP.LOW)
        up_rule = 2
        
    
    if up_rule == 0:
        print("mennään ylös")
        level_temp = round(level1)
        level_temp = int(level_temp)
        print(level1)
        for i in range(0, level_temp):
            
            GP.output(relay_switch_direction, GP.HIGH)
            GP.output(relay_up, GP.HIGH)
            time.sleep(1)
            i = i+1
    GP.output(relay_up, GP.LOW)
    GP.output(relay_switch_direction, GP.LOW)  
    return up_rule


def motor_down(down_rule): # motor controlling down direction
    print("in motorfunction")
    if down_rule == 1:
        print("ei mennä alas")
        GP.output(relay_down, GP.LOW)
        down_rule = 2

    if down_rule == 0:
        print("mennään alas")
        GP.output(relay_down, GP.HIGH)
        #down_rule = 1   
         
    return down_rule
 
def going_up(level1): #motor controlling up direction
    what_device = "going_up(level)"
    root.update()
    level1 = ask_user(level1, what_device)
    interrupt_counter = 0
    print(level1)
    up_rule = 0
    
    while True:
        print("are we really in loop")
        #top.update()
        if GP.event_detected(relay_up_limit):
                #up_rule = 1
                #print("INERRUPT TO UP")
            interrupt_counter = interrupt_counter +1
            if interrupt_counter == 2:
                up_rule = 1

        time.sleep(1)
        #up_rule = GP.input(relay_up_limit)
        #print(up_rule)
        up_rule = motor_up(up_rule)
#         temp_value = up_rule   
        if up_rule == 2:
            #GP.remove_event_detect(relay_up_limit)
            break
    return
 
 
def going_down(level1):
    what_device = "going_down(level)"
    top = Toplevel()
    top.title('interrupt controlling')
    top.configure(background="black")
    lbl = Label(top, text="push button to stop",fg="white",bg="black", font=("helvetica", 20)).pack()
    btn = Button(top, text="stop", fg="white",bg="black", font=("helvetica", 15), command=lambda: [motor_down(1), top.destroy()]).pack()
    root.update()
    level1 = ask_user(level1, what_device)
    down_rule = 0
    interrupt_counter = 0
    while True:
        top.update()
        if GP.event_detected(relay_down_limit):# this doesnt need check twice option unlike going up needs

            down_rule = 1
            print("interrupt")
            ##inerrupt_counter = interrupt_counter + 1
            #if interrupt_counter >= 2:
                #down_rule = 1
        print("are we really in loop")
        time.sleep(1)
        down_rule = motor_down(down_rule)
           
        if down_rule == 2:
            
            break
    return
 
 
def load_setup():
     return
 
 
def save_setup():
     return
 
 
def control_wlan_devices():
    root.update()
    devices = broadlink.discover(timeout=5, local_ip_address='192.168.68.118')
    print(devices)
    return
 
 
def measure_distance():
    
    print("shit sensor")
    return
 
 
def exit_and_shutdown():
    return
 
 
def exit_only():
    GP.cleanup()
    root.destroy()
    return
 
 
def main_waiting_loop():
    #label_1.configure(text = "in main loop")
    #label_1.pack()
    #measure_distance()
    return


def measure_distance():
    return


def check_updates():
    return

while True:

    measure_distance()
    main_waiting_loop()
    root.update()
    time.sleep(1)