from logging import root
from tkinter import *
from broadlink import *
from save_to_file import *
from shutdown_weatherstation import *
import broadlink # wlan plus
#from grovepi import *
import RPi.GPIO as GP
import sys
import time
import os
import smbus

trigger = 4
echo = 14
relay_down_limit = 3
relay_switch_direction = 2
relay_up_limit = 23
relay_up = 15
relay_down = 27
up_rule = 0
down_rule = 0
temp_value = 0

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
btn = Button(root, text="Adjust table up",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_up()).pack() 
btn1 = Button(root, text="Adjust table down",fg="white", bg="black",font=("helvetica", 15), command=lambda: going_down()).pack() 
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: control_wlan_devices()).pack() 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_setup()).pack() 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: load_setup()).pack() 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).pack()
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).pack() 
btn6 = Button(root, text="Check the updates",fg="white", bg="black",font=("helvetica", 15), command=lambda: measure_distance()).pack() 
label_1 = Label(root, text= "sais", font=("helvetica", 25), fg="white", bg="black")
label_1.pack()
#ultrasonic_ranger = trigger


def motor_up(up_rule):
    print("in motorfunction")
    if up_rule == 1:
        print("ei mennä ylös")
        GP.output(relay_up, GP.LOW)
        up_rule = 2
        
    
    if up_rule == 0:
        print("mennään ylös")
        GP.output(relay_up, GP.HIGH)
        #up_rule = 1
            
        
    return up_rule


def motor_down(down_rule):
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
 
def going_up():
    GP.add_event_detect(relay_up_limit, GP.RISING)
    up_rule = 0
    while True:
        print("are we really in loop")
        if GP.event_detected(relay_up_limit):
            up_rule = 1

        time.sleep(1)
        #up_rule = GP.input(relay_up_limit)
        #print(up_rule)
        up_rule = motor_up(up_rule)
#         temp_value = up_rule   
        if up_rule == 2:
            GP.remove_event_detect(relay_up_limit)
            break
    return
 
 
def going_down():
    down_rule = 0
    GP.add_event_detect(relay_up_limit, GP.RISING)
    while True:
        if GP.event_detected(relay_up_limit):
            down_rule = 1

        print("are we really in loop")
        time.sleep(1)
        #temp_value = GP.input(relay_down_limit)
        print(temp_value)
        down_rule = motor_down(down_rule)
        #temp_value = down_rule   
        if down_rule == 2: 
            break
    return
 
 
def load_setup():
     return
 
 
def save_setup():
     return
 
 
def control_wlan_devices():
     devices = broadlink.discover(timeout=5, local_ip_address='192.168.68.118')
     print(devices)
     return
 
 
def measure_distance():
    #val = ultrasonicRead(ultrasonic_ranger)
    print("shit sensor")
    return
 
 
def exit_and_shutdown():
    return
 
 
def exit_only():
    GP.cleanup()
    root.destroy()
    return
 
 
def main_waiting_loop():
    label_1.configure(text = "in main loop")
    label_1.pack()
    measure_distance()
    return


def measure_distance():
    return


def check_updates():
    return
 
measure_distance()
main_waiting_loop()
root.mainloop()