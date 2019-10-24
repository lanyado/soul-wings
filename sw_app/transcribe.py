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
from lib.ffmpeg import vid_to_flac, \
                       get_thumbnail
from lib.aws import s3_put_file
from lib.gc import gcs_put_file, \
                   call_stt, \
                   stt_res_to_json
from lib.mongo import put_to_mongo, \
                      stt_json_to_mongo_frmt, \
                      enrich_doc, \
                      update_mongo_doc
from config import MONGO_DBNAME, \
                   TRANSCRIPTS_COLL, \
                   DEFAULT_LANG, \
                   GCS_BUCKET, \
                   S3_BUCKET, \
                   THUMBNAIL_SECONDS


class Transcribe:
    """
    """

    def __init__(self,
                 path,
                 s3_bucket=S3_BUCKET,
                 gcs_bucket=GCS_BUCKET,
                 mongo_dbname=MONGO_DBNAME,
                 mongo_coll=TRANSCRIPTS_COLL,
                 language=DEFAULT_LANG,
                 user_fields=None):
        """

        :param path: (str) local path of file
        :param s3_bucket: (str) S3 bucket that files will be uploaded to
        :param gcs_bucket: (str) GCS bucket that files will be uploaded to
        :param mongo_dbname: (str) Mongo dbname to insert docs to
        :param mongo_coll: (str) Mongo collection to insert docs to
        :param language: (str) Language spoken in given file
        :param user_fields: (dict) Fields filled out by the user in upload screen
        """

        self.path = path
        self.s3_bucket = s3_bucket
        self.gcs_bucket = gcs_bucket
        self.mongo_dbname = mongo_dbname
        self.mongo_coll = mongo_coll
        self.language = language
        self.user_fields = user_fields or {}

        self.date_for_key = str(datetime.date.today()).replace('-', '/')


    def run(self):
        """
        """

        self.log = getLog('Transcribe - %s' % self.path)
        self.log.info('Start')

        self.set_mongo_oid()
        self.thumbnail_extract_and_upload()
        self.flac_conv_and_upload()
        self.handle_stt()
        self.org_upload()
        self.handle_mongo()
        self.clean_up()

        self.log.info('Done')


    def run_async(self):
        """
        Run transcribe in async thread
        """

        t = Thread(target=self.run)
        t.start()


    def thumbnail_extract_and_upload(self):
        """
        """

        self.thumbnail_key = None
        self.thumbnail_path = None

        try:
            self.thumbnail_path = get_thumbnail(self.path,
                                                THUMBNAIL_SECONDS)

        except Exception as e:
            self.log.warning('Could not extract thumbnail - error:%s', str(e))
            return

        thumbnail_file_name = str(self.mongo_oid) + '.png'
        self.thumbnail_key = 'thumbnails/{}/{}'.format(self.date_for_key,
                                                       thumbnail_file_name)

        s3_put_file(self.thumbnail_path,
                    self.s3_bucket,
                    self.thumbnail_key)


    def set_mongo_oid(self):
        """

        """

        res = put_to_mongo(self.mongo_dbname,
                           self.mongo_coll,
                           {'transcribe_complete': False})

        self.mongo_oid = res.inserted_id


    def flac_conv_and_upload(self):
        """
        """

        self.flac_path = vid_to_flac(self.path)

        flac_file_name = str(self.mongo_oid) + '.flac'
        self.flac_key = 'audio/{}/{}'.format(self.date_for_key,
                                             flac_file_name)

        s3_put_file(self.flac_path,
                    self.s3_bucket,
                    self.flac_key)
        self.gcs_blob = gcs_put_file(self.flac_path,
                                     self.gcs_bucket,
                                     flac_file_name)


    def handle_stt(self):
        """
        """

        flac_file_name = str(self.mongo_oid) + '.flac'
        res = call_stt(self.gcs_bucket,
                       flac_file_name,
                       self.language)
        self.gcs_blob.delete()

        self.json_path = os.path.splitext(self.path)[0] + '.json'
        self.stt_json = stt_res_to_json(res,
                                   self.json_path,
                                   self.user_fields)

        json_file_name = str(self.mongo_oid) + '.json'
        self.json_key = 'text/{}/{}'.format(self.date_for_key,
                                            json_file_name)

        s3_put_file(self.json_path,
                    self.s3_bucket,
                    self.json_key)


    def org_upload(self):
        """
        """

        file_ext = os.path.splitext(self.path)[1]
        org_file_name = str(self.mongo_oid) + file_ext
        self.org_key = 'original/{}/{}'.format(self.date_for_key,
                                               org_file_name)

        s3_put_file(self.path,
                    self.s3_bucket,
                    self.org_key)


    def handle_mongo(self):
        """
        """

        mongo_doc = {'s3_bucket': self.s3_bucket,
                     's3_original_key': self.org_key,
                     's3_flac_key': self.flac_key,
                     's3_json_key': self.json_key,
                     's3_thumbnail_key': self.thumbnail_key,
                     'user_fields': self.user_fields,
                     'enrichments': []}

        mongo_doc = stt_json_to_mongo_frmt(mongo_doc, self.stt_json)
        mongo_doc = enrich_doc(mongo_doc)
        mongo_doc['transcribe_complete'] = True

        update_mongo_doc(self.mongo_dbname,
                         self.mongo_coll,
                         self.mongo_oid,
                         mongo_doc)


    def clean_up(self):
        """
        """

        paths = [self.path,
                 self.flac_path,
                 self.json_path]

        for p in paths:
            if os.path.exists(p):
                os.remove(p)
