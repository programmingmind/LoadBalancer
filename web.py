#!/usr/bin/env python

from flask import Flask
from flask import render_template
from flask import Response
import glob
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return

@app.route('/graph')
def view_graphs():
    return render_template('graph.html')

@app.route('/data')
def get_aggregate_data():
    series = []
    for fileName in glob.glob("*.log"):
        with open(fileName) as f:
            data = []
            for line in f:
                vals = line.split("\t")
                data.append([int(1000 * float(vals[0])), float(vals[1]), float(vals[2])])
            series.append(dict(name=os.path.splitext(fileName)[0],data=data))

    return Response(json.dumps(series), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
