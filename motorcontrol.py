import RPi.GPIO as GP
import time
import wlan_devices
import json
from tkinter import *
from tkinter import ttk
#pins
relay_down_limit = 8
relay_switch_direction = 25
relay_up_limit = 23
relay_up = 15
relay_down = 12

trigger = 7
echo = 14
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

level1 = 0

def update_setpoint(level):#needed to update the level value
    global level1
    level1 = level
    print(level1)
    return


def measure_table(): # lets measure the desk distance from floor
    GP.output(trigger, True)
    time.sleep(0.00001)
    GP.output(trigger, False)
    StartTime = time.time()
    StopTime = time.time()
    timeout = time.time() + 0.05
    while GP.input(echo) == 0:
        StartTime = time.time()
        
        
    while GP.input(echo) == 1:
        StopTime = time.time()
    
    time.sleep(0.4)
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    distance = round(distance)
    distance = int(distance)
    return distance


def motor_control(level1, direction, limit_switch): #motor control function
    adjusting = Toplevel()
    adjusting.title("Adjustin the table")
    progressbaradj = ttk.Progressbar(adjusting, mode="indeterminate")
    progressbaradj.place(x=30, y=60, width=200)
    adjusting.geometry("300x200")
    progressbaradj.start()
    adjusting.update()
    progressbaradj.update()
    motor_temp_json = wlan_devices.get_json()
    library_tmp = json.loads(motor_temp_json)
    measure_from_floor = "distance_from_floor"
    i = measure_table() #measured distance
    print("in motor function")
    print("what is this level", level1.get())
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
            adjusting.update()
            progressbaradj.update()
            time.sleep(1)
            GP.output(direction, GP.HIGH)
            i = measure_table()
            i = round(i)
            i = int(i)
            GP.output(relay_switch_direction, GP.HIGH) #replace values            GP.output(relay_up, GP.HIGH)
            print("direction up and distance now:", i)
            if GP.event_detected(limit_switch):# 
                interrupt_clk = time.time()
                print("limit!!!")
                time.sleep(1)
                print(interrupt_clk - interrupt)
                
            
            if target_distance == i or target_distance < i:
                print("target")
                target_distance = 0
                i = 0
                level_temp = 0
                desk_level = {measure_from_floor : [i]}
                library_tmp.update(desk_level)
                break
            if target_distance == 111 or target_distance > 111: # max table high
                desk_level = {measure_from_floor : [i]}
                library_tmp.update(desk_level)
                break
            
        
    if direction == 12:#down
        target_distance = i - level_temp 
        print("target and down", target_distance)
        print(i)
        while True:
            adjusting.update()
            progressbaradj.update()
            time.sleep(1)
            GP.output(direction, GP.HIGH)
            i = measure_table()
        
            print("distance now",i)
            if GP.event_detected(limit_switch):# 
                interrupt_clk = time.time()
                print("limit!!!")
                time.sleep(1)
                print(interrupt_clk - interrupt)
            
            
            if target_distance == i or target_distance > i :
                print("target reach")
                target_distance = 0
                i = 0
                level_temp = 0
                desk_level = {measure_from_floor :[i]}
                library_tmp.update(desk_level)
                break
            if target_distance == 65 or target_distance < 65:
                print("limit reach")
                desk_level = {measure_from_floor : [i]}
                library_tmp.update(desk_level)
                break
            
    
    if direction == 15:
        GP.output(relay_switch_direction, GP.LOW) #replace values
        
    GP.output(direction, GP.LOW)
    wlan_devices.update_json(library_tmp)# when table has adjusted, we save the desk level to devices_library json value     
    progressbaradj.stop()
    adjusting.destroy()
    progressbaradj.destroy()     
    return
