import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

client = mqtt.Client()
client.connect("broker.emqx.io", 1883)
client.subscribe("/flask/mqtt")
client.on_message = on_message
client.loop_forever()