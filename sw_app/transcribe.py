"""
This Module contains functions for transcribing a video or audio file:
transcribe(path, s3_bucket, gcs_bucket, user_fields=None):
    Trancribe a given file and upload file, audio and transcript to S3
========================================================================================================================
transcribe_async(**kwargs)
    Run transcribe in async thread
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import datetime
from threading import Thread
from lib.log import getLog
from lib.ffmpeg import vid_to_flac
from lib.aws import s3_put_file
from lib.gc import gcs_put_file, \
                   call_stt, \
                   stt_res_to_json


def transcribe(path,
               s3_bucket,
               gcs_bucket,
               language,
               user_fields=None):
    """
    Trancribe a given file and upload file, audio and transcript to S3

    :param path: (str) local path of file
    :param s3_bucket: (str) S3 bucket that files will be uploaded to
    :param gcs_bucket: (str) GCS bucket that files will be uploaded to
    :param language: (str) Language spoken in given file
    :param user_fields: (dict) Fields filled out by the user in upload screen
    """

    log = getLog('Transcribe - %s' % path)
    log.info('Start')

    user_fields = user_fields or {}

    date_for_key = str(datetime.date.today()).replace('-', '/')

    file_name_with_ext = os.path.basename(path)
    file_name_no_ext = os.path.splitext(file_name_with_ext)[0]

    flac_path = vid_to_flac(path)

    org_key = 'original/{}/{}'.format(date_for_key, file_name_with_ext)
    s3_put_file(path, s3_bucket, org_key)

    flac_file_name = file_name_no_ext + '.flac'
    flac_key = 'audio/{}/{}'.format(date_for_key, flac_file_name)
    s3_put_file(flac_path, s3_bucket, flac_key)
    os.remove(path)

    gcs_blob = gcs_put_file(flac_path, gcs_bucket, flac_file_name)
    os.remove(flac_path)
    res = call_stt(gcs_bucket, flac_file_name, language)
    gcs_blob.delete()

    json_path = os.path.splitext(path)[0] + '.json'
    json_file_name = file_name_no_ext + '.json'
    stt_res_to_json(res, json_path, user_fields)

    json_key = 'text/{}/{}'.format(date_for_key, json_file_name)
    s3_put_file(json_path, s3_bucket, json_key)
    os.remove(json_path)

    log.info('Done')


def transcribe_async(**kwargs):
    """
    Run transcribe in async thread

    :param kwargs: kwargs for transcribe
    """

    t = Thread(target=transcribe, kwargs=kwargs)
    t.start()
