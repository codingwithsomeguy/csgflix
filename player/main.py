import os, json

from flask import Flask, render_template, request
app = Flask(__name__)


@app.route("/")
def home():
    # TODO: something
    return render_template("home.html", data={"foo": "bar",})


import PIL.Image
import numpy as np

@app.route("/imga/<iid>")
def imga(iid):
    iid = int(iid)
    i1 = PIL.Image.open("static/img/m1i%03d.png" % iid)
    i1a = np.array(i1).flatten()
    return json.dumps(i1a.tolist())


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

