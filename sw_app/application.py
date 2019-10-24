import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import uuid
import json
import requests
from flask import Flask, render_template, request, flash, jsonify
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin
from Transcribe import Transcribe
from search_helpers import perform_search
from Search import Search
from lib.mongo import auth_user
from lib.helpers import file_to_local_uuid_file, \
                        clean_working_dir
import config


clean_working_dir()
app = Flask(__name__, template_folder='static')


@app.route("/")
def landing_page():
    return render_template('landing_page.html')


@app.route('/upload')
def upload_file():
   return render_template('upload.html')


@app.route('/uploader', methods = ['POST'])
def uploader():
    f = request.files['file']
    path = file_to_local_uuid_file(f)
    user_fields = request.form.to_dict()
    user_fields = {k: v for k, v in user_fields.items() if v}
    language = user_fields.get('language', config.DEFAULT_LANG)
    t = Transcribe(path=path,
               s3_bucket=config.S3_BUCKET,
               gcs_bucket=config.GCS_BUCKET,
               mongo_dbname=config.MONGO_DBNAME,
               mongo_coll='transcripts',
               language=language,
               user_fields=user_fields)
    t.run_async()
    return 'file uploaded successfully, transcribing now'


@app.route('/login', methods = ['POST'])
def login():
    auth_dict = request.form.to_dict()
    auth_dict = {k: v for k, v in auth_dict.items() if v}
    auth_resp = auth_user(config.MONGO_DBNAME, config.USERS_COLL, auth_dict)

    return jsonify(auth_resp)


@app.route('/gallery', methods=['GET'])
def gallery():
    return render_template('gallery.html')


@app.route('/search', methods=['GET'])
def search_testimonies():
    return render_template('search.html')


@app.route('/results', methods=['GET'])
def search_results():
    search_dict = dict(request.args)
    search_dict = {k: v for k, v in search_dict.items() if v}
    s = Search(**search_dict)
    s.run()

    return render_template('results.html', response=s.resp_json)
