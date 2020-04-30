import os, json

from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/")
def home():
    # TODO: something
    return render_template("home.html", data={"foo": "bar",})


import PIL.Image
import numpy as np
from itertools import groupby

def rle_encode(arr):
    result = []
    for name, grp in groupby(arr):
        #print(len(list(grp)), name)
        result.append(len(list(grp)))
        result.append(name)
    return result


@app.route("/imga/<iid>")
def imga(iid):
    iid = int(iid)
    i1 = PIL.Image.open("static/img/m1i%03d.png" % iid)
    i1a = np.array(i1).flatten()
    i1a = np.array([x >> 1 for x in i1a])
    # Clamp:
    i1a[i1a <= 20] = 0
    # RLE:
    result = rle_encode(i1a.tolist())
    #return json.dumps(i1a.tolist())
    return json.dumps(result)


@app.route("/imgad/<iid>")
def imgad(iid):
    iid = int(iid)
    i1 = PIL.Image.open("static/img/m1i%03d.png" % 1)
    i1a = np.array(i1)
    i2 = PIL.Image.open("static/img/m1i%03d.png" % iid)
    i2a = np.array(i2)

    deltai = i1a ^ i2a

    return json.dumps(deltai.flatten().tolist())


import wave

@app.route("/a")
def audioarray():
    result = []
    with wave.open("static/movie1-8khz.wav") as f:
        audio_data = f.readframes(f.getnframes())
        result = list(audio_data)
    return json.dumps(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

