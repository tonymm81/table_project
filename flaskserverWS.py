import eventlet
eventlet.monkey_patch()
import eventlet.wsgi

from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from flask_sockets import Sockets
import json
import logging

logging.basicConfig(filename='flask_server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
sockets = Sockets(app)

app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 8083
app.config['MQTT_USERNAME'] = 'new_user'
app.config['MQTT_PASSWORD'] = 'passwd'
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_PROTOCOL'] = 'websockets'  
topic = '/flask/mqtt'

mqtt_client = Mqtt()
mqtt_client.init_app(app)
#mqtt_client.loop_start()

global websocket_client
websocket_client = None

@sockets.route('/ws')
def websocket(ws):
    global websocket_client
    websocket_client = ws
    while not ws.closed:
        message = ws.receive()
        if message:
            logging.info(f"Received MQTT ws publish request")
            data = json.loads(message)
            mqtt_client.publish(data['topic'], data['msg'])
            ws.send(json.dumps({'status': 'Message sent to MQTT broker'}))

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    logging.info(f"MQTT Connect status: {rc}")
    if rc == 0:
        logging.info(f"Received MQTT publish request: {userdata}")
        print('Connected successfully')
        mqtt_client.subscribe(topic)
    else:
        print('Bad connection. Code:', rc)
        logging.info(f"Error for connection")

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global websocket_client
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    logging.info(f"Received MQTT publish request: {data}")
    
    if websocket_client:
        websocket_client.send(json.dumps(data))

@app.route('/publish', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    publish_result = mqtt_client.publish(request_data['topic'], request_data['msg'])
    logging.info(f"Send message back")
    return jsonify({'code': publish_result[0]})

if __name__ == '__main__':
   
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app) 