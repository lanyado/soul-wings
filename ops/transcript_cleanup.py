"""
Deletes transcript docs that failed to transcribe.
Will only delete files with a certain age
defined by HOURS_AGO_CREATED_TRESHOLD that can be changed
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from datetime import datetime, \
                     timedelta
import pytz
from lib.helpers import get_secrets
from lib.mongo import search_mongo
from sw_app.DeleteTranscript import DeleteTranscript
import config


HOURS_AGO_CREATED_TRESHOLD = 2
SECRETS = get_secrets()


mongo_ids = search_mongo(config.MONGO_DBNAME,
                         config.TRANSCRIPTS_COLL,
                         {'transcribe_complete':False},
                         SECRETS,
                         {'_id':1})

mongo_ids = [id['_id'] for id in mongo_ids]

for id in mongo_ids:
    id_time = id.generation_time
    utcnow = datetime.utcnow().replace(tzinfo=pytz.UTC)
    time_diff = utcnow - id_time

    if time_diff >= timedelta(hours=HOURS_AGO_CREATED_TRESHOLD):
        DeleteTranscript(str(id), SECRETS).delete()
