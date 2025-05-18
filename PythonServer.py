import logging
from flask import Flask, request, jsonify
import ssl
from flask_cors import CORS


# Luo Flask-sovellus
app = Flask(__name__)
CORS(app)

# 🚀 **Loki-konfiguraatio**
logging.basicConfig(filename="/home/table/Desktop/table2/table_project/flaskserver_log.log",
                    level=logging.INFO, format="%(asctime)s - %(message)s")

# 🏗 **GET-pyyntö - palauttaa JSON-objektin**
@app.route('/data', methods=['GET'])
def get_data():
    json_data = {"message": "Hello from Raspberry Pi!", "status": "OK"}
    logging.info(f"GET-pyyntö vastaanotettu: {json_data}")
    print(f"GET vastaanotettu: {json_data}")
    return jsonify(json_data)

# 📤 **POST-pyyntö - vastaanottaa JSON-objektin ja tallentaa lokiin**
@app.route('/receive', methods=['POST'])
def receive_data():
    request_data = request.get_json()
    logging.info(f"POST-pyyntö vastaanotettu: {request_data}")
    print(f"POST vastaanotettu: {request_data}")
    
    response_data = {"received": request_data, "status": "Success"}
    return jsonify(response_data)

# 🔧 **Palvelimen käynnistys**
if __name__ == '__main__':
    context = ('/etc/ssl/certificate.crt', '/etc/ssl/private.key')  # HTTPS-sertifikaatti
    logging.info("Flask-palvelin käynnistyy...")
    print("Flask-palvelin käynnistyy...")
    app.run(host='0.0.0.0', port=5000, ssl_context=context)