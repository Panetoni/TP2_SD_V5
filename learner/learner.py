import os
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
RESOURCE_PATH = "/shared_data/resource.txt"
learner_id = os.getenv("LEARNER_ID", "learner-1")

@app.route('/learn', methods=['POST'])
def learn():
    tid = request.json["tid"]
    value = request.json["value"]
    try:
        # Escreve os dados no resource.txt, incluindo a mensagem (se houver)
        with open(RESOURCE_PATH, "a") as f:
            f.write(f"TID: {tid}, Client: {value['client_id']}, Timestamp: {value['timestamp']}, Message: {value.get('message', '')}\n")
        print(f"[{learner_id}] Recurso atualizado com TID {tid}")
        try:
            response = requests.post(
                f"http://{value['client_addr']}/committed",
                json={"tid": tid},
                timeout=2
            )
            if response.status_code != 200:
                print(f"[{learner_id}] Falha ao notificar cliente {value['client_addr']}")
        except requests.exceptions.RequestException as e:
            print(f"[{learner_id}] Erro ao notificar cliente: {str(e)}")
        return jsonify({"status": "OK"})
    except Exception as e:
        print(f"[{learner_id}] Erro crítico: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/read', methods=['GET'])
def read_resource():
    try:
        with open(RESOURCE_PATH, "r") as f:
            return f.read(), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists(RESOURCE_PATH):
        open(RESOURCE_PATH, "w").close()
    app.run(host='0.0.0.0', port=5000)
