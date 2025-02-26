import os
from threading import Lock
from flask import Flask, jsonify, request

app = Flask(__name__)

# ID único para o acceptor
acceptor_id = os.getenv("ACCEPTOR_ID", "acceptor-1")

class AcceptorState:
    def __init__(self):
        self.lock = Lock()
        self.promised_tid = None
        self.accepted_tid = None
        self.accepted_value = None

    def _convert_tid(self, tid):
        try:
            parts = tid.split('-')
            # Exemplo: "acceptor-1-3" -> (3, "acceptor-1")
            return (int(parts[-1]), '-'.join(parts[:-1]))
        except (ValueError, IndexError):
            return (0, tid)

    def prepare(self, tid):
        with self.lock:
            current_tid = self._convert_tid(tid)
            current_promised = self._convert_tid(self.promised_tid) if self.promised_tid else (0, '')
            if current_tid > current_promised:
                self.promised_tid = tid
                return {
                    "promise": True,
                    "last_accepted_tid": self.accepted_tid,
                    "last_accepted_value": self.accepted_value
                }
            else:
                return {
                    "promise": False,
                    "hint": f"Already promised to TID: {self.promised_tid}"
                }

    def accept(self, tid, value):
        with self.lock:
            if tid == self.promised_tid:
                self.accepted_tid = tid
                self.accepted_value = value
                return {"accepted": True}
            return {"accepted": False}

acceptor_state = AcceptorState()

@app.route('/prepare', methods=['POST'])
def handle_prepare():
    data = request.json
    response = acceptor_state.prepare(data['tid'])
    print(f"[{acceptor_id}] Received PREPARE for TID {data['tid']} - Response: {response}")
    return jsonify(response)

@app.route('/accept', methods=['POST'])
def handle_accept():
    data = request.json
    response = acceptor_state.accept(data['tid'], data['value'])
    print(f"[{acceptor_id}] Received ACCEPT for TID {data['tid']} - Response: {response}")
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
