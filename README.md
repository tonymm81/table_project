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

plan: if i dont find problem i have to change different code. Or instead pack() use grid() command to all buttons and labels.

plan: how to check wlan devices status. first you havew to figureout wich device. then use value.get_state() (pulbs) and check_power() whith wlan plugs.
biggest problem is to check witch devices status you want to check. 

plan: how to check device, use devtype and index number. this how you can check what device to control. this how you can find correct ip to control devices