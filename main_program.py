from logging import root
from tkinter import *
from broadlink import *
from save_to_file import *
from shutdown_weatherstation import *
import broadlink # wlan plugs
#from grove.gpio import GPIO
#from grovepi import *
import RPi.GPIO as GP
import sys
import time
import os
import smbus

trigger = 4
echo = 15
relay_down_limit = 23
relay_switch_direction = 2
relay_up_limit = 3
relay_up = 14
relay_down = 17

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
GP.setup(relay_down_limit, GP.IN, pull_up_down=GP.PUD_DOWN)
GP.setup(relay_up_limit, GP.IN, pull_up_down=GP.PUD_DOWN)

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


 
def going_up():
     return
 
 
def going_down():
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
