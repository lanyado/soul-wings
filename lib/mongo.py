

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import re
import pymongo
from proj_secrets import secrets
from lib.log import getLog
import lib.helpers as helpers
from config import TERM_TYPE_MAP, \
                   OPERATOR_MAP, \
                   DEFAULT_CONTEXT_BLOCK_SIZE, \
                   MONGO_DBNAME, \
                   DEFAULT_OPERATOR
from enrichments import enrichments


LOG = getLog('MONGO')


def get_coll_conn(dbname, coll):
    """
    Returns a connection to mentioned collection

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :return: (pymongo.collection.Collection)
    """

    db_conn = pymongo.MongoClient(secrets.mongo_endpoint)[dbname]
    coll_conn = db_conn[coll]

    return coll_conn


def put_to_mongo(dbname, coll, doc):
    """
    Upload doc to mongo

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param doc: (dict) doc as dict
    :return: (pymongo.results.InsertOneResult) Mongo response
    """

    conn = get_coll_conn(dbname, coll)
    res = conn.insert_one(doc)

    LOG.info('Put to MONGO - %s - %s - %s', dbname, coll, res.inserted_id)

    return res


def update_mongo_doc(dbname, coll, id, content):
    """
    Update mongo doc based on id

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param id: (bson.objectid.ObjectId) mongo OID
    :param content: (dict) Content to update in the doc
    :return: (pymongo.results.UpdateResult) Mongo response
    """

    conn = get_coll_conn(dbname, coll)
    res = conn.update_one({'_id': id}, {'$set': content})

    LOG.info('Updated doc - %s - %s - %s', dbname, coll, id)

    return res


def search_mongo(dbname, coll, query):
    """
    Run search on MONGO and return results

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param query: (dict) mongo query as dict
    :return: (pymongo.cursor.Cursor) MONGO cursor for iterating over results
    """

    conn = get_coll_conn(dbname, coll)
    res = conn.find(query)

    LOG.info('Ran Query - %s - %s - %s', dbname, coll, query)

    return res


def get_query_part(term):
    """
    Get query part based on term type

    :param term: (dict)
    :return: (dict) MONGO query part
    """

    return TERM_TYPE_MAP[term['type']](term['term'])


def build_query(operator=DEFAULT_OPERATOR,
                terms=None,
                kv_pairs=None):
    """
    Builds mongo query from given params

    :param terms: (list of dicts) result from search_string_to_terms
    :param operator: (str) Operator that will act in the query (and \ or)
    :param kv_pairs: (dict) Key Value pairs to add to the query
    :return: (dict) MONGO query body
    """

    terms = terms or []
    kv_pairs = kv_pairs or {}
    operator = OPERATOR_MAP.get(operator)
    query = {operator: []}

    for t in terms:
        query_part = get_query_part(t)
        query[operator].append(query_part)

    for k, v in kv_pairs.items():
        query[operator].append({k: v})

    return query


def auth_user(dbname, coll, auth_dict):
    """
    Auth user against coll and return bool

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param auth_dict: (dict) Dict with user details for query
    :return: (bool) True if exists \ False if not
    """

    conn = get_coll_conn(dbname, coll)
    query = build_query('and', kv_pairs=auth_dict)
    res = search_mongo(dbname, coll, query)
    res = [d for d in res]

    resp_json = {'auth': False}

    if len(res) != 0:
        resp_json['auth'] = True
        resp_json['user_id'] = str(res[0].get('_id', ''))

    return resp_json


def stt_json_to_mongo_frmt(doc, stt_json):
    """
    Converts STT JSON to MONGO formatted doc

    :param doc: (dict) Doc body with existing keys
    :param json_obj: (dict) STT JSON
    :return: (dict) doc as dict
    """

    words = []

    for res in stt_json['results']:
        words += helpers.get_best_alt(res.get('alternatives'))

    words = [helpers.lower_all_vals(w) for w in words]

    transcript = ' '.join([w.get('word', '') for w in words])

    doc['words'] = words
    doc['transcript'] = transcript

    return doc


def enrich_doc(doc):
    """
    Search for all enrichments in transcript and add matches to doc body

    :param doc: (dict) doc as dict
    :return: (dict) Formatted doc
    """

    for e in enrichments:
        if e['value'] in doc['transcript']:
            doc['enrichments'].append(e)

    return doc
