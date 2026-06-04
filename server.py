from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def score():

    return jsonify({
        "p1": 3,
        "p2": 7
    })

app.run(host="0.0.0.0", port=5000)