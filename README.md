# table_project

This project is for adjusment of table level from floor. It has also graphical interface where you can control the desk level and wlan plugs and bulbs.

it has rasbperry pi4, 7 inch touch screen, uln2804 chip, three relays and resistors. there is also gearbox motor what lift or lower the desk.
ultrasonic sensor measures the desk distance from floor and you can save your favorite setup and load it later. We can save all light and plugs setup and distance from floor.

ver 100
just setting upsystems.

ver101
limit switches areworking well. software stops when the limit switch state turns 1. also motor powering is working well. uln chip works well.
i dont haveultrasonic sensor yetbutthey are one rule also. user can set themeasurement to adjust the table. 
but we continue the planning and developing

bug:
-up and down limit interrupt pin are not working as i hope. i have to figure out what is the problem here. I was ordering the better ultrasonic sensors from china
i dont know why you cannot buy this versions from finland. That one what i buy from local shop was bad version. It demands own controlling board. 

plan:
perhaps inerruptpin has to check out twice is it true before it can give an order to stop the motor controlling. a also add graphical button where user
can stop the motor. I also want to build up the radio button where user can choose table distanse or how much it gonna rise or going down.

ver102
added the slider where user can choose what is table distance from floor. limits are now working but i have to plan out how to control motor based on measurement.
perhaps i build up totally different motorcontrol function. This how we can do less lines of code.


ver 103:
deleted motor_up and motor_down function. also changed going up and going down functions. testing and figureout the bugs. now changes are made and lots of code deleted.
bug: motorcontrol function doesnt work so perhaps probles is there that i have to control code flow where program goes after user choose the measurement.

ver 104:
table control works no and limit switches working also. i update the function ask user to control motor, and this how everything works now.
plan: i dont know what should i do next. saveto file with obect orieted programming style or should i do next lamp controlling?

ver 105:
update graphics to wlan devices and also make a search function to wlan devices so its easy to update if wanted.

ver 106:
table adjusment is now working with ultrasonic sensor. limit Interrupt has not working yet. I have to figure out what is the best way to do this. 

ver 107:
added scrollbar on search wlan devices. there is also buttons what is created by number of wlan devices.

bug:
scrollbar wont work on down side. upside yes
-tested mainloop function
-tested changing packing options.
-tested to connect window to root
-tested buttons has correct pieces. button name is not what i want but i have to fix this. in graphics button shows right name
-testet to loop canvas
-testin to change window side
-tested different scrollbar
- tested to left top level and put scroll canvas to root. works fine
-tested to use grid command on buttons. error comes. no grid command on slavve label
-tested also place function. not helping, buttons gone somewhere

fixed: scrollbar works only on root
plan: if i dont find problem i have to change different code. Or instead pack() use grid() command to all buttons and labels.


plan: how to check wlan devices status. first you havew to figureout wich device. then use value.get_state() (pulbs) and check_power() whith wlan plugs.
biggest problem is to check witch devices status you want to check. 

plan: how to check device, use devtype and index number. this how you can check what device to control. this how you can find correct ip to control devices

bug: some how older device ip address still stays same even the device is different(fixed)
bug: when finding the ip address from string this re findall was not good choice(fixed)
bug: now the devices name and ip address is saving to json value but somehow the state of device wont work.(fixed)
fixed earlier bug, now device state is saved on json string. 

ver108:
plan:
- if i make program this how: in beging of program it search all wlandevices and keeps a json value where you can command devices. and i have to make a update button if some how some device wont show on the button list.
- a have to also make a text field what shows wlan devices state.
- i have to also make new window to bulps. there will be somesliders where you can change bulp state and colormode.
- if sp4 broadlinkhas some enegry measuring option perhapsi should show it also. (optional)

bug: distance measurement wont work on control_motor function. tested earlier but now stopped working.(sometimes) tested twice but not done this

bug: else klause print out again some labels. to fix this use if elif else clause, not two if clause (fixed, not tested)

plan:
i make a control_wlan_devices(devices, devices_name, devices_library). when user push a button it opens a top window where you can change the wlan device status. also i have to made own window to bulps where you can adjust the colors etc.
problem. when i make a devices button, i have to figure out how to save device name per button that i can use devices name in control wlan devices function. 

- if i make a 20 buttons already. then in for loop we sahe the infoemation to buttons.. and in the sametime we store the device name to button value and use it to function call
- i update the button define to json value at the same time when you save the devices information. If you try to open this part json it complains key error p. 

ver109:
- wlan devices button works fine. buttons are controlling to correct function. i insert buttons to json library and make them to graphics with for loop. this how i can save devices name to value what we send to function where we change devices state

plan: next we do controlling to devices. i have to make window where we can change the devices state. also to bulps we have to make a slider on colors and brightness.
also we have to do error handling whenwe check the wlan device status.
bug: fix button letter sizes
bug: table measurement wont update on label. (fixed)
bug: sometimes program crash if wlan devices timeout comes. (plan try exept function)(fixed)

ver110:
plan. 
- i have to figure out that how to remove all .pack() command becausae this wont allow me to place buttons and sliders how i want them. So next big move is get rid of place command. you cannot use anything else commands with pack() command. 
- i was planning to use .grid() command where you can define button, slider, labels location on graphics.
- also i have to fixed the measuring distance from main label. i wont work.
- on wlan plugs i have to make only two buttons and label what shows devices state
- also i have to get rid of global values but it might not easy, because graphics is behiving differently than regural program.
- when i using in bulps the sliders, i need to conifuge the siledrs wint command option. this how the user changes will show immeadiately. other i have to make a update buttons on graphics
- this changes is so big that i have to make a different program to make this changes. so in git this file is main_program_ver110.py
- i have to figure out how to get interrupt pin to work. perhaps oscilosscope will show if there is some disturb signal. some how the interrupt wont work because it will acticvate without reason.
- make a function what search right device to command. This has to be done because you cannot store in json value this kind of information.

testing:  
-main root windows pack() command is moved now. test if thats okay to slave windows if there is some pack commands how it works.

test result. label and buttons are different position. the slider is right side. this canvas is quite small. i have to figure out why it is so small
its only half of top window 
sideplan:
-perhaps i have to change button colors only??if doing this, you have to change the search wlan devices function where you define the button colors..or in controlling function?

report:
- fixed the bugs, now buttons show correctly. also function controlling in bulb window works fine. i replace all pack() command to grid(). grid is good because you can give exact coordinates to buttons. 
- i have to figure out how to command devices on cotrol_wlan_devices function. broadlink uses tuple typed list(solved)
- now light controlling is working. Do here if clause what check devices status, also update json value based on devices state.(solved)

bug: try exept clause gives an error, try to solve this before version number change. TypeError: catching classes that do not inherit from BaseException is not allowed
bug: json object wont updated from bulb controlling function(solved, json library is now global and it work fine)
bug: wlan devices button wont destroy the wlan devices list windows, says only that top3  are not define


plan: 
- now i have to fugure out how to update in json value devices state. (control function shows correcty but search_wlan_devices wont.)(solved, json library is now global and it work fine)
- name sliders in controlling window
- figure out how to control windows that thos label colors will change if devices state is changed.
- remove the device str from json library.(solved)
- figure out how to takea value from slider and do things about it(solved)
- wlan bulbs wont work on rgb adjusment, only brightness works. figure out why

report:
added json update(not tested)
button controlling made this how that wlan devices should update now from json file(not tested)
wlan bulb controlling working, wlan switces working
add back json library

added max and min distance where you can adjust the table on ask user function. make also software limit to max and min positions.




