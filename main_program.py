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
temp_value = 0
level1 = 0

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
GP.add_event_detect(relay_up_limit, GP.RISING)
GP.add_event_detect(relay_down_limit, GP.RISING)

def update_setpoint(level):
    global level1
    level1 = level
    print(level1)
    return

def ask_user(level, direction, limit_switch):
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
def motor_control(level1, direction, limit_switch):# not tested!!!!!!!!!
    print("in motor function")
    level_temp = level1.get()
    level_temp = round(level_temp)
    level_temp = int(level_temp)
    print(level1)
    interrupt = 0
    for i in range(0, level_temp): # insert here limit switch
        GP.output(direction, GP.HIGH)
        time.sleep(1)
        i = i+1
        if direction == 15:
            GP.output(relay_switch_direction, GP.HIGH) #replace values            GP.output(relay_up, GP.HIGH)
            print("direction up")
            
        print("going down")
        if GP.event_detected(limit_switch):# replace value
            interrupt = interrupt +1
            print("limit!!!")
            if interrupt == 2:
                
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
    return
 
 
def going_down(): # make a function call to control motor
    global level1
    root.update()
    direction = 12
    limit_switch = 8
    level1 = ask_user(level1, direction, limit_switch)
    #motor_control(level1, "relay_down", "relay_down_limit")
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
