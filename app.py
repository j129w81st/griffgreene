from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Route to serve index.html
@app.route("/")
def home():
    return send_from_directory(".", "index.html")  # Use "." to serve from current folder

# Route to serve all static files (HTML files)
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
