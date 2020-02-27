"""
This Module contains Google Cloud helper functions:
gcs_put_file(local_path, gcs_bucket, gcs_path)
    Upload a given file to GCS and return blob obj
========================================================================================================================
gcs_del_file(gcs_bucket, gcs_path)
    Delete a given file from GCS
========================================================================================================================
call_stt(gcs_bucket, gcs_path)
    Call Google STT and get transcript for given GCS path
========================================================================================================================
stt_res_to_json(res, path, user_fields)
    Save STT result to JSON and return path
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from time import sleep
import json
import codecs
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage
from google.protobuf.json_format import MessageToDict
from lib.log import getLog
from config import LANGUAGE_CODE_MAP


LOG = getLog('GC')


def gcs_put_file(local_path,
                 gcs_bucket,
                 gcs_path):
    """
    Upload a given file to GCS

    :param local_path: (str) local path of file to upload
    :param gcs_bucket: (str) GCS bucket name
    :param gcs_path: (str) Path in bucket to upload to
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(gcs_bucket)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)

    LOG.info('Put to GCS - %s - %s/%s', local_path, gcs_bucket, gcs_path)


def gcs_del_file(gcs_bucket,
                 gcs_path):
    """
    Delete a given file from GCS

    :param gcs_bucket: (str) GCS bucket name
    :param gcs_path: (str) Path in bucket to delete file from
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(gcs_bucket)
    blob = bucket.delete_blob(gcs_path)

    LOG.info('Deleted from GCS - %s/%s', gcs_bucket, gcs_path)


def call_stt(gcs_bucket,
             gcs_path,
             language):
    """
    Call Google STT and get transcript for given GCS path

    :param gcs_bucket: (str) GCS bucket name
    :param gcs_path: (str) Path of file in bucket
    :return: (protobuf response) stt API response result
    """

    language_code = LANGUAGE_CODE_MAP.get(language)

    if not language_code:
        raise Exception('language code not found')

    gcs_uri = 'gs://{}/{}'.format(gcs_bucket, gcs_path)

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        enable_word_time_offsets=True,
        language_code=language_code)

    operation = client.long_running_recognize(config, audio)

    while not operation.done():
        sleep(10)

    response = operation.result()

    LOG.info('Got STT - %s/%s', gcs_bucket, gcs_path)

    return response


def stt_res_to_json(res,
                    path,
                    user_fields):
    """
    Save STT result to JSON and return path

    :param res: (protobuf response) stt API response result
    :param path: (str) local path to save the file to
    :param user_fields: (dict) Fields filled out by the user in upload screen
    :return: (dict) STT res as dict
    """

    serialized = MessageToDict(res)
    serialized['user_fields'] = user_fields

    json_file = codecs.open(path, 'w', encoding='utf-8')
    json.dump(serialized, json_file, ensure_ascii=False)
    json_file.close()

    LOG.info('Saved JSON - %s', path)

    return serialized
