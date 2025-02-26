import os
import sys
import time
import threading
import requests
from flask import Flask, request, jsonify

# Servidor para receber notificações de commit
notification_app = Flask(__name__)

@notification_app.route('/committed', methods=['POST'])
def committed():
    data = request.json
    tid = data.get('tid')
    print(f"\n[Notification] Write operation COMMITTED with TID: {tid}")
    return jsonify({"status": "received"}), 200

def run_notification_server():
    notification_app.run(
        host='0.0.0.0',
        port=int(os.getenv("CLIENT_PORT", "5001")),
        debug=False,
        use_reloader=False
    )

class InteractiveClient:
    def __init__(self, client_id, proposers):
        self.client_id = client_id
        self.proposers = proposers
        self.client_addr = f"{os.getenv('CLIENT_HOSTNAME', 'client')}:{os.getenv('CLIENT_PORT', '5001')}"
        self.should_exit = False
    
    def register(self):
        proposer = self.proposers[0]
        try:
            response = requests.post(
                f"http://{proposer}:5000/register",
                json={"client_id": self.client_id, "client_addr": self.client_addr},
                timeout=2
            )
            if response.status_code == 200:
                print(f"[Cliente {self.client_id}] Registrado com sucesso.")
            else:
                print(f"[Cliente {self.client_id}] Falha no registro.")
        except Exception as e:
            print(f"[Cliente {self.client_id}] Erro ao registrar: {str(e)}")

    def deregister(self):
        proposer = self.proposers[0]
        try:
            response = requests.post(
                f"http://{proposer}:5000/deregister",
                json={"client_id": self.client_id},
                timeout=2
            )
            if response.status_code == 200:
                print(f"[Cliente {self.client_id}] Removido com sucesso da rede.")
            else:
                print(f"[Cliente {self.client_id}] Falha ao remover da rede.")
        except Exception as e:
            print(f"[Cliente {self.client_id}] Erro ao remover: {str(e)}")

    def send_write_request(self):
        proposer = self.proposers[0]
        timestamp = int(time.time())
        # Solicita a mensagem ao usuário
        message = input("Digite a mensagem para enviar: ")
        data = {
            "client_id": self.client_id,
            "timestamp": timestamp,
            "client_addr": self.client_addr,
            "message": message  # novo campo para a mensagem
        }
        try:
            response = requests.post(
                f"http://{proposer}:5000/propose",
                json=data,
                timeout=2
            )
            if response.status_code == 200:
                tid = response.json().get("tid", "unknown")
                print(f"[Cliente {self.client_id}] Write request COMMITTED (TID: {tid})")
            else:
                print(f"[Cliente {self.client_id}] Write request FAILED")
        except Exception as e:
            print(f"[Cliente {self.client_id}] Erro ao contactar proposer: {str(e)}")


    def check_resource(self):
        learner = "learner-1"  # ou use uma lista se desejar balancear
        try:
            response = requests.get(f"http://{learner}:5000/read", timeout=2)
            print("\n=== Conteúdo Atual do Recurso ===")
            print(response.text)
            print("==================================")
        except Exception as e:
            print(f"[Cliente {self.client_id}] Erro ao ler recurso: {str(e)}")

def start_interactive_client(client):
    while not client.should_exit:
        print("\nOptions:")
        print("1. Write to resource")
        print("2. Read resource")
        print("3. Exit and deregister")
        print("4. Close interface (stay in network)")
        choice = input("Choose an option: ")

        if choice == "1":
            client.send_write_request()
        elif choice == "2":
            client.check_resource()
        elif choice == "3":
            client.deregister()
            client.should_exit = True
            os._exit(0)  # Sai completamente
        elif choice == "4":
            print("\nInterface closed. Client remains active in network.")
            print("Use 'docker attach <container_name>' to reopen interface.")
            return  # Sai da interface mas mantém o processo
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    client_id = os.getenv("CLIENT_ID", "client-1")
    proposers = ["proposer-1"]
    
    # Inicia o servidor de notificações em thread não-daemon
    notification_thread = threading.Thread(
        target=run_notification_server,
        daemon=False
    )
    notification_thread.start()
    
    # Mantém o processo principal ativo
    client = InteractiveClient(client_id, proposers)
    client.register()
    
    while True:
        start_interactive_client(client)
        # Loop vazio para manter o processo ativo
        while True:
            time.sleep(1)