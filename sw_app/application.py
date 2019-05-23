from flask import Flask, render_template, request, flash
from werkzeug import secure_filename
import requests
from transcribe import transcribe
import uuid
import json
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
    search_term = request.form['search_line']
    url = "https://soulwings.search.windows.net/indexes/azureblob-index/docs"
    headers = {
      "api-key": "F01491A07C517D0BD467CAA8AEF2FE35",
      "Content-Type": "application/json"
    }
    params = {
      "api-version": "2019-05-06",
      "search": search_term
    }
    response_json = requests.get(url, params=params, headers=headers).json()
    search_results = response_json['value']
    number_of_results = len(search_results)
    files_uuid = [result['metadata_storage_name'].split(".")[0] for result in search_results]
    video_url = "https://soulwings.blob.core.windows.net/videos/"
    files_urls = [video_url + file_uuid + ".mp4" for file_uuid in files_uuid]
    return render_template('results.html',search_line=files_urls)
