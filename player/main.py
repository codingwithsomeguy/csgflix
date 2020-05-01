import os, json

from flask import Flask, render_template, request, Response
app = Flask(__name__)


@app.route("/")
def home():
    # TODO: something
    return render_template("home.html", data={"foo": "bar",})


@app.route("/cdn/movie/<moviefile>")
def cdn_movie(moviefile):
    print("fake_cdn:", moviefile)
    # TODO: don't do this
    result = open("../encoding/media/encoded/" + moviefile).read()
    return Response(result, mimetype="text/json")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

