import os, json, sys

from flask import Flask, render_template, request, Response
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("ui.html", data={"foo": "bar",})

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
    # TODO: something
    return render_template("player.html",
        data={"cdnbaseurl": "/cdn/movie/",})


#TODO: dump the two cdn routines
# added - identical to cdn_movie, but image type for boxart
# (avoids needing to copy to static)
@app.route("/cdn/boxart/<moviefile>")
def cdn_boxart(moviefile):
    print("fake_cdn:", moviefile)
    # TODO: don't do this
    result = open("../encoding/media/encoded/" + moviefile, "rb").read()
    return Response(result, mimetype="image/png")


@app.route("/cdn/movie/<moviefile>")
def cdn_movie(moviefile):
    print("fake_cdn:", moviefile)
    # TODO: don't do this
    result = open("../encoding/media/encoded/" + moviefile).read()
    return Response(result, mimetype="text/json")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        app.run(debug=True, host="0.0.0.0", port=int(sys.argv[1]))
    else:
        app.run(debug=True, host="0.0.0.0")
