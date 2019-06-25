import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import uuid
import json
import requests
from flask import Flask, render_template, request, flash, jsonify
from transcribe import transcribe_async
from search_helpers import perform_search
from lib.helpers import file_to_local_uuid_file, \
                        clean_working_dir
import config


clean_working_dir()
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
      path = file_to_local_uuid_file(f)
      user_fields = request.form.to_dict()
      user_fields = {k: v for k, v in user_fields.items() if v}
      language = user_fields.get('lang', config.DEFAULT_LANG)
      transcribe_async(path=path,
                       s3_bucket=config.S3_BUCKET,
                       gcs_bucket=config.GCS_BUCKET,
                       language=language,
                       user_fields=user_fields)
      return 'file uploaded successfully, transcribing now'


@app.route('/search', methods=['GET', 'POST'])
def search_testimonies():
    return render_template('search.html')


@app.route('/results', methods=['GET', 'POST'])
def search_results():
    search_term = request.form['search_line']
    res = jsonify(perform_search(search_term))
    return res
