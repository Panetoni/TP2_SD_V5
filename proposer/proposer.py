import os
import requests
from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Utiliza a variável de ambiente para definir o ID único do proposer
proposer_id = os.getenv("PROPOSER_ID", "proposer_1")

# Altere para usar os nomes individuais dos acceptors:
acceptors = ["tp2_sd_v5_acceptor_1", "tp2_sd_v5_acceptor_2", "tp2_sd_v5_acceptor_3"]
# E para os learners:
learners = ["tp2_sd_v5_learner_1", "tp2_sd_v5_learner_2"]

registered_clients = {}  # client_id -> client_addr

@app.route('/propose', methods=['POST'])
def handle_propose():
    client_data = request.json  # Pegando os dados do cliente
    if not client_data:
        return jsonify({"status": "error", "message": "Request body missing"}), 400

    print(f"[{proposer_id}] Proposta recebida: {client_data}")  # Log para debug

    # Extraindo e logando a mensagem enviada pelo cliente (se houver)
    message = client_data.get("message", "")
    if message:
        print(f"[{proposer_id}] Mensagem do cliente: {message}")

    tid = generate_tid()

    # Fase Prepare: envia para todos os acceptors
    promises = []
    for acceptor in acceptors:
        try:
            response = requests.post(
                f"http://{acceptor}:5000/prepare",
                json={"tid": tid, "proposer_id": proposer_id},
                timeout=2
            )
            if response.json().get("promise"):
                promises.append(response.json())
        except Exception as e:
            print(f"[{proposer_id}] Erro em prepare no {acceptor}: {e}")
            continue

    # Quorum: exige (n/2 + 1) respostas (nesse exemplo, 2 de 3)
    if len(promises) >= 2:
        accepted = []
        for acceptor in acceptors:
            try:
                response = requests.post(
                    f"http://{acceptor}:5000/accept",
                    json={
                        "tid": tid,
                        "value": client_data,  # Inclui todos os dados, inclusive "message"
                        "proposer_id": proposer_id
                    },
                    timeout=2
                )
                if response.json().get("accepted"):
                    accepted.append(acceptor)
            except Exception as e:
                print(f"[{proposer_id}] Erro em accept no {acceptor}: {e}")
                continue

        if len(accepted) >= 2:
            # Notifica os learners para commitar o valor
            for learner in learners:
                try:
                    requests.post(
                        f"http://{learner}:5000/learn",
                        json={
                            "tid": tid,
                            "value": client_data,
                            "client_addr": client_data.get("client_addr")
                        },
                        timeout=2
                    )
                except Exception as e:
                    print(f"[{proposer_id}] Erro notificando learner {learner}: {e}")
            return jsonify({"status": "COMMITTED", "tid": tid}), 200

    return jsonify({"status": "FAILED"}), 400

def generate_tid():
    # Gera um TID baseado no timestamp em milissegundos, garantindo que seja único e crescente.
    return f"{proposer_id}-{int(time.time() * 1000)}"

# Endpoints para registrar/deregistrar clientes
@app.route('/register', methods=['POST'])
def register_client():
    data = request.json
    client_id = data.get("client_id")
    client_addr = data.get("client_addr")
    if client_id and client_addr:
        registered_clients[client_id] = client_addr
        print(f"[{proposer_id}] Cliente registrado: {client_id} -> {client_addr}")
        return jsonify({"status": "registered"}), 200
    return jsonify({"status": "error", "message": "Dados incompletos"}), 400

@app.route('/deregister', methods=['POST'])
def deregister_client():
    data = request.json
    client_id = data.get("client_id")
    if client_id in registered_clients:
        del registered_clients[client_id]
        print(f"[{proposer_id}] Cliente removido: {client_id}")
        return jsonify({"status": "deregistered"}), 200
    return jsonify({"status": "not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
