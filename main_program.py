from logging import root
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
btn2 = Button(root, text="Control the lights and wlan plugs",fg="white", bg="black",font=("helvetica", 15), command=lambda: control_wlan_devices()).pack() 
btn3 = Button(root, text="Save this setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: save_setup()).pack() 
btn3 = Button(root, text="Load setup",fg="white", bg="black",font=("helvetica", 15), command=lambda: load_setup()).pack() 
btn4 = Button(root, text="Exit and shutdown the weatherstation",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_and_shutdown()).pack()
btn5 = Button(root, text="Exit this system",fg="white", bg="black",font=("helvetica", 15), command=lambda: exit_only()).pack() 
btn6 = Button(root, text="Check the updates",fg="white", bg="black",font=("helvetica", 15), command=lambda: measure_distance()).pack() 
label_1 = Label(root, text= "sais", font=("helvetica", 25), fg="white", bg="black")
label_1.pack()
#ultrasonic_ranger = trigger


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
    #top = Toplevel()
    #top.title('Wlan devices')
    #top.geometry("850x500")
    #top.configure(background="black")
    #scrollbar = Scrollbar(top)
    #scrollbar.pack( side = RIGHT, fill = Y )
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
    #top.update()
    #root.update()
    devices = broadlink.discover(timeout=5, local_ip_address='192.168.68.118')
    print(len(devices))
    device_names = []
    for o in range (len(devices)):
        device_names.append(devices[o].name)
        print(device_names[o])
        o = o +1
    
    #test labels
    
    rounds = 0
    for i in range (len(devices)):
        # make here buttons what change number of devices
        infolabel = Label(second_frame, text=device_names[rounds])
        infolabel.pack(pady=0, padx=0)
        btn = device_names[i] 
        btn = Button(second_frame, text = btn, command = lambda: [second_frame.destroy(), main_frame.destroy()], bg = "black", fg = "white")
        print("lap", i, "name" ,btn, "devicename", device_names[i])
        if (rounds % 2) == 1:
            btn.pack( pady=0, padx=8)
        else:
            btn.pack(pady=0, padx=0)
        #btn.place(x=100, y=100)
        #top.update()
        i = i +1
        rounds = rounds +1
        #break
        
    #top.mainloop()
    second_frame.mainloop()
    return devices
 
 
def load_setup():
     return
 
 
def save_setup():
     return
 
 
def control_wlan_devices(): # plan this next. graphical view and how to show listed devices.
    devices = []
    root.update()
    devices = search_all_devices_wlan(devices)
    print(devices)
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


devices = broadlink.discover(timeout=5, local_ip_address='192.168.68.118')
while True:
#    root.update()
#
    main_waiting_loop()
    root.update()
##    time.sleep(1)
#main_waiting_loop() # not helping scroll problem
#root.mainloop()