from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to the Soul-Wings platform!"

@app.route("/upload")
def upload_testimony():
    return "Upload your testimony"

@app.route("/search")
def upload_testimony():
    return "Search for testimonies"
