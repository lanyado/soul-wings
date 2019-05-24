from flask import Flask, render_template, request, flash
from werkzeug import secure_filename
import requests
from transcribe import transcribe
from search_helpers import perform_search
import uuid
import json
import os


app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

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

      user_fields = request.form.to_dict()
      user_fields['fileName'] = f.filename

      transcribe(path_to_file, user_fields)
      return 'file uploaded successfully'


@app.route('/search', methods=['GET', 'POST'])
def search_testimonies():
    return render_template('search.html')


@app.route('/results', methods=['GET', 'POST'])
def search_results():
    search_term = request.form['search_line']
    return perform_search(search_term)
