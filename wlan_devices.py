from broadlink import *
import broadlink
import json
import traceback
import pprint
from tkinter import *
import re
from motorcontrol import measure_table



   

devices_library = {}
devices = []
json.dumps(devices_library, indent=4)

def save_json(devices_library):
    with open("devices.json", "w") as f:
        json.dump(devices_library, f, indent=4)

def load_json():
    try:
        with open("devices.json", "r") as f:
            return json.load(f)  # Lataa JSON-tiedostosta
    except FileNotFoundError:
        return {}  # Jos tiedostoa ei ole, palautetaan tyhjä


def get_json():
    global devices_library
    devices_library = load_json()
    return json.dumps(devices_library, indent=4) 


def update_json(device_library_temp):
    global devices_library
    devices_library = device_library_temp#json.dumps(device_library_temp, indent=4)
    save_json(device_library_temp)
    #pprint.pprint(devices_library) # easier way to read json value
    return

def check_wlan_device_status(devices): # check here also buttons and save device in button command
   
    devices_library_temp = get_json()
    temp_json = json.loads(devices_library_temp)
    buttons_row = 15
    for i in range (len(devices)):
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
            bulb_button = temp_name +" = Button(second_frame, text = btn, command = lambda: wlan_devices.control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
            bulb_pack = temp_name+ ".grid(row ="+str(buttons_row)+", column=2)" 
            if len(bulb_ip) < 9:
                bulb_ip = result_bulb[4]
                
            result_bulb.clear()
            print(bulb_ip, bulbname)
            try:
                devices_temp1 = broadlink.discover(timeout=5, discover_ip_address=bulb_ip)
                devices_temp1[0].auth()
                device_state1 = devices_temp1[0].get_state()
                 
            except Exception as e:
                print("device communication failed", e)
                
           
                
            bulb_library = {bulbname : [bulb_ip,  device_state1, devtype, bulb_button, bulb_pack]}#temp value to json
            temp_json.update(bulb_library)
            
            
        if devtype == 30073 or devtype == 42348:
            sp4_button = " "
            sp4_pack = " "
            sp4_name = devices[i].name
            size = len(sp4_name)
            sp4_temp_name = sp4_name[:size-3]
            temp_str_sp4 = devices[i]
            temp_str_sp4 = str(temp_str_sp4)
            result_sp4 = re.findall(r'[\d\.]+', temp_str_sp4)
            sp4_button = sp4_temp_name +" = Button(second_frame, text = btn, command = lambda: wlan_devices.control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
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
            except Exception as e:
                print("device communication failed", e)
            
            
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
                
            sp3_button = sp3_temp_name +" = Button(second_frame, text = btn, command = lambda: wlan_devices.control_wlan_devices("+"'" +devices[i].name+ "'"+", devices), bg = 'black', fg = 'white')" #devicename has to include " "
            sp3_pack = sp3_temp_name +".grid(row ="+str(buttons_row)+", column=2)"
            print(sp3_ip, sp3_name)
            result_sp3.clear()
            try:
                devices_temp3 = broadlink.discover(timeout=5, discover_ip_address=sp3_ip)
                devices_temp3[0].auth()
                #print(devices[0])
                device_state3 = devices_temp3[0].check_power()

            except Exception as e:
                print("device communication failed", e)
            
            sp3_library = {sp3_name : [sp3_ip, device_state3, devtype, sp3_button, sp3_pack]} #temp value to json
            temp_json.update(sp3_library)
            
            
            
        devtype = 0
        buttons_row = buttons_row + 3
     
    table_distance = measure_table(14, 7)
    desk_level = {"distance_from_floor" : [table_distance]}
    temp_json.update(desk_level)
    #devices_library = json.dumps(temp_json)
    update_json(temp_json)
    #print(devices_library)
    
    return 


def control_wlan_devices(device_names, devices):# here we change the wlan devices state   
    devices_library_temp_control = get_json() 
    device_name_tmp = device_names
    temp_json = json.loads(devices_library_temp_control)
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
        control = SearchSpecific_device(device_name_tmp, devices)
        """for i in range(len(devices)):
            if device_name_tmp == devices[i].name:
                control = devices[i]
                print(control)
                break"""
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
        #root.update()
        top2.mainloop()
    else:
       
        print("plug!!")
        control = SearchSpecific_device(device_name_tmp, devices)
        """for i in range(len(devices)):
            if device_name_tmp == devices[i].name:
                control = devices[i]
                break"""
            
        control.auth()
        switch_state = control.check_power()
        
        if switch_state == True:
            control.set_power(False)
            
        elif switch_state == False:
            control.set_power(True)
            
    switch_state = control.check_power()
    temp_json[device_name_tmp][1] = switch_state
    #devices_library = json.dumps(temp_json, indent=4)
    update_json(temp_json)
    #device_name_tmp=""
    return 


def SearchSpecific_device(device_name_tmp, devices):
    control = ""
    for i in range(len(devices)):
        if device_name_tmp == devices[i].name:
            control = devices[i]
            break
            
    return control


def set_state_bulp(temp_json,device_name_tmp, control, colors, choice):
    value_number = choice
    value_number = int(value_number)
    colors_ = str(colors)
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
    print("lamp case", device_name_tmp)
    temp_json[device_name_tmp][1]['pwr'] = state['pwr']
    #print("whole json" ,temp_json[device_name_tmp])
    #print("testing", device_name_tmp, "json", str(temp_json[device_name_tmp][1]['pwr']))
    #devices_library = json.dumps(temp_json, indent=4)
    update_json(temp_json)
    return 
    