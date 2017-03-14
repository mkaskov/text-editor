#! /usr/bin/env python

# by PureMind

from flask import Flask, request, jsonify
from flask_cors import CORS
from util import textUtil as tu

# Obtain the flask app object
app = Flask(__name__)
CORS(app)

@app.route('/ner/parse/search', methods=['POST'])
def entry_point():
    query = request.json['query']
    query = tu.decode_from_java(query)
    with open("collectData/collectNerData.txt", "a") as text_file:
        text_file.write("[line]"+query+"\n")
    return jsonify(answer="")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=False, threaded=False)
