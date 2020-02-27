import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from bson.objectid import ObjectId
from lib.mongo import delete_from_mongo
from lib.aws import s3_list_objects, \
                    s3_delete_key
from config import MONGO_DBNAME, \
                   TRANSCRIPTS_COLL, \
                   S3_BUCKET


class DeleteTranscript:
    """
    Class for Deleting Transcipts

    Methods
    -------
    delete()
        Delete doc from Mongo and the correlating S3 files
    """

    def __init__(self,
                 id,
                 secrets,
                 s3_bucket=S3_BUCKET,
                 mongo_dbname=MONGO_DBNAME,
                 mongo_coll=TRANSCRIPTS_COLL):
        """
        Init DeleteTranscript

        :param id: (str) mongo OID
        :param secrets: (dict) Result from helpers.get_secrets
        :param s3_bucket: (str) S3 bucket that files will be uploaded to
        :param mongo_dbname: (str) Mongo dbname to insert docs to
        :param mongo_coll: (str) Mongo collection to insert docs to
        """

        self.id = id
        self.secrets = secrets
        self.s3_bucket = s3_bucket
        self.mongo_dbname = mongo_dbname
        self.mongo_coll = mongo_coll


    def delete(self):
        """
        Delete doc from Mongo and the correlating S3 files
        """

        keys = s3_list_objects(self.s3_bucket,
                               self.secrets)

        for key_data in keys:
            key = key_data.get('Key', '')
            if self.id in key:
                s3_delete_key(self.s3_bucket,
                              key,
                              self.secrets)
                continue

        delete_from_mongo(self.mongo_dbname,
                          self.mongo_coll,
                          ObjectId(self.id),
                          self.secrets)
