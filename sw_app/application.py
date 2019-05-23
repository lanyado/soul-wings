from flask import Flask, render_template, request
from werkzeug import secure_filename
app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to the Soul-Wings platform!"

@app.route("/upload")
def upload_testimony():
    return "Upload your testimony"

@app.route("/search")
def search_testimonies():
    return "Search for testimonies"
