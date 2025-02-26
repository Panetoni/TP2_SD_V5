from flask import Flask, jsonify, request
# from datetime import datetime
from threading import Lock

app = Flask(__name__)

class AcceptorState:
    def __init__(self):
        self.lock = Lock()
        self.promised_tid = None         # Maior TID prometido
        self.accepted_tid = None         # Maior TID aceito
        self.accepted_value = None       # Valor aceito

    def prepare(self, tid):
        """Lógica de preparação do Paxos"""
        try:
            # Converte TID string para tuple comparável (timestamp, proposer_id)
            tid_parts = tid.split('_')
            converted_tid = (int(tid_parts[-1]), '_'.join(tid_parts[:-1]))
            
            current_promised = (self.promised_tid.split('_')[-1], '_'.join(self.promised_tid.split('_')[:-1])) if self.promised_tid else (0, '')
            
            # Comparação hierárquica de TIDs
            if converted_tid > current_promised:
                self.promised_tid = tid
                response = {
                    "promise": True,
                    "last_accepted_tid": self.accepted_tid,
                    "last_accepted_value": self.accepted_value
                }
            else:
                response = {
                    "promise": False,
                    "hint": f"Já prometi para TID maior: {self.promised_tid}"
                }
        except Exception as e:
            response = {"promise": False, "error": str(e)}
        
        return response

    def accept(self, tid, value):
        """Lógica de aceitação do Paxos"""
        if tid == self.promised_tid:
            self.accepted_tid = tid
            self.accepted_value = value
            return {"accepted": True}
        else:
            return {"accepted": False, "reason": "TID não corresponde ao prometido"}

acceptor_state = AcceptorState()

@app.route('/prepare', methods=['POST'])
def handle_prepare():
    data = request.json
    tid = data['tid']
    print(f"📩 Prepare request recebido - TID: {tid}")
    
    response = acceptor_state.prepare(tid)
    print(f"📤 Resposta Prepare: {response}")
    
    return jsonify(response)

@app.route('/accept', methods=['POST'])
def handle_accept():
    data = request.json
    response = acceptor_state.accept(data['tid'], data['value'])
    print(f"📥 Accept request - TID: {data['tid']} | Resposta: {response}")
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)