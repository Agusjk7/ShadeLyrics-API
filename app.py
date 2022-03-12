from os import getenv

from flask import jsonify, render_template

from website import create_app

app = create_app()


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"msg": "Endpoint not found.", "status": 404}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"msg": "Method not allowed.", "status": 405}), 405


if __name__ == "__main__":
    app.run(debug=False, port=int(getenv("PORT", 5000)))
