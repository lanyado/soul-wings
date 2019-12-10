import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
sys.path.append(REPO_DIRECTORY)

from enrichments import enrichments as ens

WORKING_DIR = '{}/working_dir'.format(REPO_DIRECTORY)

S3_BUCKET = 'soul-wings'

GCS_BUCKET = 'soul-wings'

MONGO_DBNAME = 'soul-wings'

TRANSCRIPTS_COLL = 'transcripts'

USERS_COLL = 'users'

DEFAULT_CONTEXT_BLOCK_SIZE = 21

THUMBNAIL_REL_TIME = 0.5 # Fraction of total media time to get thumbnail

DEFAULT_LANG = 'hebrew'

DEFAULT_OPERATOR = 'and'

LANGUAGE_CODE_MAP = {'hebrew': 'he-IL'}

TERM_TYPE_MAP = {'single': lambda t: {"transcript": {'$regex': t}},
                 'qouted': lambda t: {"transcript": {'$regex': t}}}

OPERATOR_MAP = {'and': '$and',
                'or': '$or'}

TOKEN_TIMEOUT_HOURS = 168 # 1 week

ENRICHMENT_TYPES = set([e['type'] for e in ens])

SECRETS_S3_DETAILS = ('soul-wings-secrets', 'secrets.json')
