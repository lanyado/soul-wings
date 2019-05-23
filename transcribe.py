import os
import uuid
import json
import codecs
import secrets
import subprocess
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage
from google.protobuf.json_format import MessageToDict
from azure.storage.file import FileService


GCS_BUCKET = 'soulwings'
AZ_STORAGE_ACCOUNT = 'soulwings'
AZ_STORAGE_SHARE = 'soulwings'
AZ_STORAGE_FOLDER = None


def az_get_file(share, folder, file_name):
    """
    Downloads file from azure storage and returns local path
    """

    local_path = os.getcwd() + '/' + file_name
    file_service = FileService(account_name=AZ_STORAGE_ACCOUNT,
                               account_key=secrets.AZ_STORAGE_KEY)
    file_service.get_file_to_path(share, folder, file_name, local_path)

    return local_path


def az_put_file(share, folder, local_path):
    """
    Uploads file to azure storage and returns local path
    """

    file_name = os.path.basename(local_path)
    file_service = FileService(account_name=AZ_STORAGE_ACCOUNT,
                               account_key=secrets.AZ_STORAGE_KEY)
    file_service.create_file_from_path(share, folder, file_name, local_path)


def vid_to_flac(path, **kwargs):
    """
    Converts video to mono flac and returns flac path
    """

    flac_path = os.path.splitext(path)[0] + '.flac'
    if os.path.isfile(flac_path):
        os.remove(flac_path)

    ffmpeg_call = 'ffmpeg -i "{}" -f flac -ac 1 -vn "{}"'.format(path, flac_path)
    subprocess.call(ffmpeg_call, shell=True)

    return flac_path


def upload_to_gcs(local_path, bucket, gcs_path):
    """
    Upload a given file to GCS and return blob obj
    """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)

    return blob


def call_stt(bucket, gcs_path):
    """
    Call Google STT and get transcript for given GCS path
    """

    gcs_uri = 'gs://{}/{}'.format(bucket, gcs_path)

    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=gcs_uri)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        enable_word_time_offsets=True,
        language_code='he-IL')

    operation = client.long_running_recognize(config, audio)
    response = operation.result()

    return response


def stt_res_to_json(res, path):
    """
    Save STT result to JSON and return path
    """

    serialized = MessageToDict(res)

    json_path = os.path.splitext(path)[0] + '.json'
    json_file = codecs.open(json_path, 'w', encoding='utf-8')
    json.dump(serialized, json_file, ensure_ascii=False)
    json_file.close()

    return json_path


def transcribe(path):
    """
    Trancribe a given file and upload the sound
    and transcript to azure storage
    """

    file_name = os.path.basename(path)

    flac_path = vid_to_flac(path)
    az_put_file(AZ_STORAGE_SHARE, AZ_STORAGE_FOLDER, path)
    az_put_file(AZ_STORAGE_SHARE, AZ_STORAGE_FOLDER, flac_path)
    os.remove(path)

    gcs_blob = upload_to_gcs(flac_path, GCS_BUCKET, file_name)
    os.remove(flac_path)
    res = call_stt(GCS_BUCKET, file_name)
    gcs_blob.delete()

    json_path = stt_res_to_json(res, path)
    az_put_file(AZ_STORAGE_SHARE, AZ_STORAGE_FOLDER, json_path)
    os.remove(json_path)
