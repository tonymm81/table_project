import websocket

ws = websocket.WebSocket()
ws.connect("ws://raspberrypi-ip:5000/ws")
ws.send("Test message")
print(ws.recv())
ws.close()