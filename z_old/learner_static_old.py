# learner/learner.py
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/learn', methods=['POST'])
def learn():
    tid = request.json["tid"]
    value = request.json["value"]
    client_addr = request.json["client_addr"]
    
    # Simular escrita no recurso R (arquivo compartilhado)
    with open("/shared_data/resource.txt", "a") as f:
        f.write(f"TID: {tid}, Client: {value['client_id']}, Timestamp: {value['timestamp']}\n")
    
    # Notificar cliente
    requests.post(f"http://{client_addr}/committed", json={"tid": tid})
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)