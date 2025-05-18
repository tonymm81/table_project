import paho.mqtt.client as mqtt

client = mqtt.Client()
client.username_pw_set("new_user", "passwd")
client.connect("localhost", 8083, 60)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("/flask/mqtt")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()