import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from lib.mongo import org_filter_wrap_and_search
from lib.aws import get_s3_url
from config import MONGO_DBNAME, \
                   TRANSCRIPTS_COLL


class Gallery:
    """
    Class for generating results for the gallery endpoint

    Attributes
    ----------
    resp_json : (dict)
        response json for frontend
        keys: videos (list of dicts)

    Methods
    -------
    run()
        Run Search, format results and save results to self.resp_json
    """

    def __init__(self,
                 secrets,
                 user_info=None,
                 mongo_dbname=MONGO_DBNAME,
                 mongo_coll=TRANSCRIPTS_COLL):
        """
        Init Gallery

        :param secrets: (dict) Result from helpers.get_secrets
        :param user_info: (dict) user info dict from TokenHandler
        :param mongo_dbname: (str) Mongo dbname for conn
        :param mongo_coll: (str) Relevant coll in each doc for query
        """

        self.secrets = secrets
        self.user_info = user_info or {}
        self.mongo_dbname = mongo_dbname
        self.mongo_coll = mongo_coll


    def run(self):
        """
        Run Search, format results and save results to self.resp_json
        """

        res = self._get_user_gallery_docs()
        self._frmt_for_html(res)


    def _get_user_gallery_docs(self):
        """
        Get gallery info that the user can see based on the users organization

        :return: (pymongo.cursor.Cursor) MONGO cursor for iterating over results
        """

        query = {"transcribe_complete":True}
        project = {"s3_bucket":1,
                   "s3_original_key":1,
                   "s3_thumbnail_key":1,
                   "user_fields":1}

        return org_filter_wrap_and_search(self.mongo_dbname,
                                          self.mongo_coll,
                                          query,
                                          self.secrets,
                                          project,
                                          self.user_info)


    def _frmt_for_html(self,
                       res):
        """
        Format Mongo result for frontend

        :param res: (pymongo.cursor.Cursor) Mongo query result
        :set attr: resp_json (dict) response json for frontend
        """

        frmt_for_html = []

        for vid in res:
            vid_obj = {}

            vid_bucket = vid.get('s3_bucket', '')
            s3_original_key = vid.get('s3_original_key', '')
            s3_thumbnail_key = vid.get('s3_thumbnail_key', '')
            vid_obj['s3_original_url'] = get_s3_url(vid_bucket,
                                                 s3_original_key)
            vid_obj['s3_thumbnail_url'] = get_s3_url(vid_bucket,
                                                  s3_thumbnail_key)

            user_fields = vid.get('user_fields', {})
            for k, v in user_fields.items():
                vid_obj[k] = v
            frmt_for_html.append(vid_obj)

        self.resp_json = {'videos':frmt_for_html}
