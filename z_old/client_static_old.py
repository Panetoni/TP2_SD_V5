# client/client.py
import requests
import time
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
client_id = "client_1"  # Será sobrescrito via Docker
proposer = "proposer1"

@app.route('/committed', methods=['POST'])
def committed():
    print(f"Transação {request.json['tid']} confirmada!")
    return jsonify({"status": "OK"})

def start_client():
    for _ in range(random.randint(10, 50)):
        timestamp = int(time.time())
        data = {
            "client_id": client_id,
            "timestamp": timestamp,
            "client_addr": f"client{client_id.split('_')[1]}:5000"
        }
        response = requests.post(f"http://{proposer}:5000/propose", json=data)
        time.sleep(random.randint(1, 5))

if __name__ == "__main__":
    threading.Thread(target=start_client).start()
    app.run(host='0.0.0.0', port=5000)