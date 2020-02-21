import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from datetime import date
from threading import Thread
from sw_app.DeleteTranscript import DeleteTranscript
from lib.log import getLog
from lib.ffmpeg import vid_to_flac, \
                       get_thumbnail
from lib.aws import s3_put_file
from lib.gc import gcs_put_file, \
                   call_stt, \
                   stt_res_to_json
from lib.mongo import put_to_mongo, \
                      stt_json_to_mongo_frmt, \
                      update_mongo_doc
from config import MONGO_DBNAME, \
                   TRANSCRIPTS_COLL, \
                   DEFAULT_LANG, \
                   GCS_BUCKET, \
                   S3_BUCKET, \
                   THUMBNAIL_REL_TIME
from enrichments import enrichments


class Transcribe:
    """
    Class for transcribing media files and uploading them to S3 and Mongo

    Attributes
    ----------
    Attributes are documented in each relevant func.
    No attributes are used by initiating code later on.

    Methods
    -------
    run(self)
        Run transcription process
    run_async(self)
        Run transcription process in async thread
    """

    def __init__(self,
                 path,
                 secrets,
                 s3_bucket=S3_BUCKET,
                 gcs_bucket=GCS_BUCKET,
                 mongo_dbname=MONGO_DBNAME,
                 mongo_coll=TRANSCRIPTS_COLL,
                 language=DEFAULT_LANG,
                 user_fields=None):
        """
        Init Transcribe

        :param path: (str) local path of file
        :param secrets: (dict) Result from helpers.get_secrets
        :param s3_bucket: (str) S3 bucket that files will be uploaded to
        :param gcs_bucket: (str) GCS bucket that files will be uploaded to
        :param mongo_dbname: (str) Mongo dbname to insert docs to
        :param mongo_coll: (str) Mongo collection to insert docs to
        :param language: (str) Language spoken in given file
        :param user_fields: (dict) Fields filled out by the user in upload screen
        """

        self.path = path
        self.secrets = secrets
        self.s3_bucket = s3_bucket
        self.gcs_bucket = gcs_bucket
        self.mongo_dbname = mongo_dbname
        self.mongo_coll = mongo_coll
        self.language = language
        self.user_fields = user_fields or {}

        self.date_for_key = str(date.today()).replace('-', '/')


    def run(self):
        """
        Run transcription process
        """

        try:
            self.log = getLog('Transcribe - %s' % self.path)
            self.log.info('Start')

            self._set_mongo_oid()
            self._thumbnail_extract_and_upload()
            self._flac_conv_and_upload()
            self._handle_stt()
            self._org_upload()
            self._handle_mongo()
            self._clean_up()

            self.log.info('Done')

        except Exception as e:
            self.log.error(str(e))
            self._clean_up()
            raise


    def run_async(self):
        """
        Run transcription process in async thread
        """

        t = Thread(target=self.run)
        t.start()


    def _set_mongo_oid(self):
        """
        Creates Mongo doc and returns the OID of the created doc

        This is needed in order to perform cleanups in the future
        All files are uploaded to S3 with keys including this OID
        When performing cleanups we will be able to see docs
        that are marked as False and delete \ investigate all their responding files

        :set attr: mongo_oid (bson.objectid.ObjectId) mongo OID of created doc
        """

        res = put_to_mongo(self.mongo_dbname,
                           self.mongo_coll,
                           {'transcribe_complete': False},
                           self.secrets)

        self.mongo_oid = res.inserted_id


    def _thumbnail_extract_and_upload(self):
        """
        Extract thumbnail from video and upload to S3

        :set attr: thumbnail_key (str) S3 key of thumbnail
                   thumbnail_path (str) local path of thumbnail
        """

        self.thumbnail_key = None
        self.thumbnail_path = None

        try:
            self.thumbnail_path = get_thumbnail(self.path,
                                                THUMBNAIL_REL_TIME)

        except Exception as e:
            self.log.warning('Could not extract thumbnail - error:%s', str(e))
            return

        thumbnail_file_name = str(self.mongo_oid) + '.png'
        self.thumbnail_key = 'thumbnails/{}/{}'.format(self.date_for_key,
                                                       thumbnail_file_name)

        s3_put_file(self.thumbnail_path,
                    self.s3_bucket,
                    self.thumbnail_key,
                    self.secrets)


    def _flac_conv_and_upload(self):
        """
        Convert media to mono FLAC and upload to S3

        :set attr: flac_key (str) S3 key of FLAC file
                   flac_path (str) local path of FLAC file
                   gcs_blob (bucket.blob) gcs file obj
        """

        self.flac_path = vid_to_flac(self.path)

        flac_file_name = str(self.mongo_oid) + '.flac'
        self.flac_key = 'audio/{}/{}'.format(self.date_for_key,
                                             flac_file_name)

        s3_put_file(self.flac_path,
                    self.s3_bucket,
                    self.flac_key,
                    self.secrets)
        self.gcs_blob = gcs_put_file(self.flac_path,
                                     self.gcs_bucket,
                                     flac_file_name)


    def _handle_stt(self):
        """
        Handle GC STT call and upload JSON to S3

        :set attr: json_key (str) S3 key of JSON file
                   json_path (str) local path of JSON file
                   stt_json (dict) STT res as dict
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
                    self.json_key,
                    self.secrets)


    def _org_upload(self):
        """
        Upload original user file to S3

        :set attr: org_key (str) S3 key of original user file
        """

        file_ext = os.path.splitext(self.path)[1]
        org_file_name = str(self.mongo_oid) + file_ext
        self.org_key = 'original/{}/{}'.format(self.date_for_key,
                                               org_file_name)

        s3_put_file(self.path,
                    self.s3_bucket,
                    self.org_key,
                    self.secrets)


    def _enrich_doc(self,
                    mongo_doc):
        """
        Search for all enrichments in transcript and add matches to doc body

        :param mongo_doc: (dict) doc as dict
        :return: (dict) Formatted doc
        """

        for e in enrichments:
            if e['value'] in mongo_doc['transcript']:
                mongo_doc['enrichments'].append(e)

        return mongo_doc


    def _handle_mongo(self):
        """
        Handle formatting and updating existing Mongo Doc
        """

        mongo_doc = {'s3_bucket': self.s3_bucket,
                     's3_original_key': self.org_key,
                     's3_flac_key': self.flac_key,
                     's3_json_key': self.json_key,
                     's3_thumbnail_key': self.thumbnail_key,
                     'user_fields': self.user_fields,
                     'enrichments': []}

        mongo_doc = stt_json_to_mongo_frmt(mongo_doc, self.stt_json)
        mongo_doc = self._enrich_doc(mongo_doc)
        mongo_doc['transcribe_complete'] = True

        update_mongo_doc(self.mongo_dbname,
                         self.mongo_coll,
                         self.mongo_oid,
                         mongo_doc,
                         self.secrets)


    def _clean_up(self):
        """
        Delete all files that the process created locally, in S3 and the mongo doc
        """

        if getattr(self, 'mongo_oid', None):
            DeleteTranscript(str(self.mongo_oid),
                             self.secrets,
                             self.s3_bucket,
                             self.mongo_dbname,
                             self.mongo_coll).delete()

        path_attrs = ['path',
                      'flac_path',
                      'json_path',
                      'thumbnail_path']

        paths = [getattr(self, p) for p in path_attrs if getattr(self, p, None)]

        for p in paths:
            if os.path.exists(p):
                os.remove(p)
