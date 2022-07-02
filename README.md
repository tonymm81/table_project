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
deleted motor_up and motor_down function. also changed going up and going down functions. testing and figureout the bugs.