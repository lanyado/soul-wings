from flask import Flask, render_template, request, flash
from werkzeug import secure_filename
from ..transcribe import transcribe
import uuid
import os


app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to the Soul-Wings platform!"

@app.route('/upload')
def upload_file():
   return render_template('upload.html')


@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
      f = request.files['file']
      uuid_file = '%s.mp4' %uuid.uuid4()
      f.save(secure_filename(uuid_file))
      path_to_file = '%s/%s' %(os.getcwd(),uuid_file)
      transcribe(path_to_file)
      return 'file uploaded successfully'


@app.route('/search', methods=['GET', 'POST'])
def search_testimonies():
    return render_template('search.html')


@app.route('/results', methods=['GET', 'POST'])
def search_results():
    search_line = request.form['search_line']
    return render_template('results.html',search_line=search_line)
