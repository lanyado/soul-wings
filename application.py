import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
sys.path.append(REPO_DIRECTORY)

from flask import Flask, render_template, request, jsonify, url_for
from sw_app.Transcribe import Transcribe
from sw_app.TokenHandler import TokenHandler
from sw_app.Search import Search
from sw_app.Gallery import Gallery
from lib.mongo import auth_user
from lib.helpers import file_to_local_uuid_file, \
                        clean_working_dir, \
                        get_secrets
from lib.log import getLog
import config


SECRETS = get_secrets()

clean_working_dir()
application = Flask(__name__, template_folder='static')
token_handler = TokenHandler()


@application.route("/")
def landing_page():
    """
    Render landing_page.html

    :return: (str) html for frontend
    """

    return render_template('landing_page.html')


@application.route("/about_us")
def about_us():
    """
    Render about.html

    :return: (str) html for frontend
    """

    return render_template('about_us.html')


@application.route("/about")
@token_handler.auth_request
def about():
    """
    Render about.html

    :return: (str) html for frontend
    """

    return render_template('about.html')


@application.route('/uploader', methods = ['POST'])
def uploader():
    """
    Receive user file and start transcription process

    :return: (flask.wrappers.Response) json response for frontend
        keys: upload_successful (bool)
    """

    try:
        trans_log = getLog('Transcribe')

        resp = {'upload_successful': False}

        f = request.files['file']
        path = file_to_local_uuid_file(f)
        user_fields = request.form.to_dict()
        user_fields = {k: v for k, v in user_fields.items() if v}
        language = user_fields.get('language', config.DEFAULT_LANG)
        print(request.form.getlist('tags'))
        '''
        t = Transcribe(path=path,
                       secrets=SECRETS,
                       s3_bucket=config.S3_BUCKET,
                       gcs_bucket=config.GCS_BUCKET,
                       mongo_dbname=config.MONGO_DBNAME,
                       mongo_coll=config.TRANSCRIPTS_COLL,
                       language=language,
                       user_fields=user_fields)
        t.run_async()
        '''
        resp['upload_successful'] = True


    except Exception as e:
        trans_log.error('error:%s' % e, exc_info=True)

    return jsonify(resp)


@application.route('/login', methods = ['POST'])
def login():
    """
    Auth user against mongo, gen token and return token

    :return: (flask.wrappers.Response) json response for frontend
        keys: auth (bool) - IF AUTH FAILED
        keys: redirect_url (str), user_token (str)
    """

    auth_dict = request.form.to_dict()
    auth_dict = {k: v for k, v in auth_dict.items() if v}
    user_token = auth_user(config.MONGO_DBNAME,
                           config.USERS_COLL,
                           auth_dict,
                           token_handler,
                           SECRETS)

    if user_token:
        resp = {'redirect_url':url_for('search_testimonies'),
                'user_token': user_token}

    else:
        resp = {'auth':False}

    return jsonify(resp)


@application.route('/gallery', methods=['GET'])
@token_handler.auth_request
def gallery():
    """
    Fetch gallery for user and render gallery.html with response

    response (dict) - see Gallery.resp_json for docs

    :return: (str) html for frontend
    """

    g = Gallery(secrets=SECRETS,
                mongo_dbname=config.MONGO_DBNAME,
                mongo_coll=config.TRANSCRIPTS_COLL)
    g.run()

    return render_template('gallery.html', response=g.resp_json)


@application.route('/search', methods=['GET'])
@token_handler.auth_request
def search_testimonies():
    """
    Render search.html

    :return: (str) html for frontend
    """

    return render_template('search.html')


@application.route('/results', methods=['GET'])
@token_handler.auth_request
def search_results():
    """
    Perform search against mongo based on user request
    and render results.html with response

    response (dict) - see Search.resp_json for docs

    :return: (str) html for frontend
    """

    search_dict = dict(request.args)
    search_dict = {k: v for k, v in search_dict.items() if v}
    s = Search(secrets=SECRETS,
               **search_dict)
    s.run()

    return render_template('results.html', response=s.resp_json)


if __name__ == "__main__":
    application.run()
