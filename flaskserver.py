
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)

app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1884
app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 60  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True
topic = '/flask/mqtt'

mqtt_client = Mqtt(app)
global websocket_client
websocket_client = None

@sockets.route('/ws')
def websocket(ws):
    global websocket_client
    websocket_client = ws  # Tallennetaan WebSocket-yhteys
    while not ws.closed:
        message = ws.receive()
        if message:
            data = json.loads(message)
            mqtt_client.publish(data['topic'], data['msg'])
            ws.send(json.dumps({'status': 'Message sent to MQTT broker'}))




@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)  # subscribe topic
    else:
        print('Bad connection. Code:', rc)

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global websocket_client
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    
    if websocket_client:
        websocket_client.send(json.dumps(data))  # Käytetään tallennettua WebSocket-yhteyttä

@app.route('/publish', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    publish_result = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



