import os, json, sys

from flask import Flask, render_template, request, Response, g
app = Flask(__name__)


def get_cdn_url():
    if 'cdn' not in g:
        g.cdn_url = "/static/cdn/"
    return g.cdn_url


@app.route("/")
def home():
    return render_template("ui.html", data={"cdnbaseurl": get_cdn_url(),})


@app.route("/search/<searchquery>")
def search(searchquery):
    result = []
    # added catalog.json to fetchcorpus.py
    catalog_file = "../encoding/media/original/catalog.json"
    catalog = json.load(open(catalog_file))
    cKeys = list(catalog.keys())
    #result.append(catalog[cKeys[3]])
    #result.append(catalog[cKeys[4]])
    for titleid, meta in catalog.items():
        if meta["synopsis"].find(searchquery) >= 0:
            result.append(meta)
        #print("titleid: " + titleid, meta["synopsis"])

    return Response(json.dumps(result[0:2]), mimetype="text/json")


@app.route("/play")
def play():
    return render_template("player.html",
        data={"cdnbaseurl": get_cdn_url(),})


@app.route("/metric")
def metric():
    if "d" in request.args:
        try:
            metrics_obj = json.loads(request.args["d"])
            print("metrics data:", metrics_obj)
        except ValueError:
            pass

    return "OK"


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app.run(debug=True, host="0.0.0.0", port=int(sys.argv[1]))
    else:
        app.run(debug=True, host="0.0.0.0")
