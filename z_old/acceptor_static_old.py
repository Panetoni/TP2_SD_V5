# acceptor/acceptor.py
from flask import Flask, jsonify, request

app = Flask(__name__)
highest_tid = None
accepted_value = None

@app.route('/prepare', methods=['POST'])
def prepare():
    global highest_tid
    tid = request.json["tid"]
    proposer_id = request.json["proposer_id"]
    
    if (highest_tid is None) or (tid > highest_tid):
        highest_tid = tid
        return jsonify({
            "promise": True,
            "last_accepted_tid": highest_tid,
            "last_accepted_value": accepted_value
        })
    else:
        return jsonify({"promise": False})

@app.route('/accept', methods=['POST'])
def accept():
    global highest_tid, accepted_value
    tid = request.json["tid"]
    value = request.json["value"]
    
    if tid == highest_tid:
        accepted_value = value
        return jsonify({"accepted": True})
    else:
        return jsonify({"accepted": False})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)