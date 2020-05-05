"""
This Module contains Mongo helper functions:
get_coll_conn(dbname, coll, secrets)
    Returns a connection to mentioned collection
========================================================================================================================
put_to_mongo(dbname, coll, doc, secrets)
    Upload doc to mongo
========================================================================================================================
update_mongo_doc(dbname, coll, id, content, secrets)
    Update mongo doc based on id
========================================================================================================================
search_mongo(dbname, coll, query, secrets, project)
    Run search on MONGO and return results
========================================================================================================================
get_query_part(term)
    Get query part based on term type
========================================================================================================================
get_query_part(term)
    Get query part based on term type
========================================================================================================================
build_query(operator, terms, kv_pairs)
    Builds mongo query from given params
========================================================================================================================
auth_user(dbname, coll, auth_dict, token_handler, secrets)
    Auth user against coll and return token or None if not authorized
========================================================================================================================
stt_json_to_mongo_frmt(doc, stt_json)
    Converts STT JSON to MONGO formatted doc
========================================================================================================================
delete_from_mongo(dbname, coll, id, secrets)
    Delete doc from mongo
========================================================================================================================
org_filter_wrap_and_search(dbname, coll, query, secrets, project, user_info)
    Wraps a given mongo query with an organization filter and executes the query
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import pymongo
from lib.log import getLog
import lib.helpers as helpers
from config import TERM_TYPE_MAP, \
                   OPERATOR_MAP, \
                   DEFAULT_OPERATOR, \
                   EXCLUDE_KEYS_FROM_AUTH_QUERY, \
                   COLL_USER_ID_FIELD_MAP


LOG = getLog('MONGO')


def get_coll_conn(dbname,
                  coll,
                  secrets):
    """
    Returns a connection to mentioned collection

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param secrets: (dict) Result from helpers.get_secrets
    :return: (pymongo.collection.Collection)
    """

    mongo_endpoint = secrets.get('mongo_endpoint')
    db_conn = pymongo.MongoClient(mongo_endpoint)[dbname]
    coll_conn = db_conn[coll]

    return coll_conn


def put_to_mongo(dbname,
                 coll,
                 doc,
                 secrets):
    """
    Upload doc to mongo

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param doc: (dict) doc as dict
    :param secrets: (dict) Result from helpers.get_secrets
    :return: (bson.objectid.ObjectId) mongo OID
    """

    conn = get_coll_conn(dbname, coll, secrets)
    res = conn.insert_one(doc)

    LOG.info('Put to MONGO - %s - %s - %s', dbname, coll, res.inserted_id)

    return res


def update_mongo_doc(dbname,
                     coll,
                     id,
                     content,
                     secrets):
    """
    Update mongo doc based on id

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param id: (bson.objectid.ObjectId) mongo OID
    :param content: (dict) Content to update in the doc
    :param secrets: (dict) Result from helpers.get_secrets
    :return: (pymongo.results.UpdateResult) Mongo response
    """

    conn = get_coll_conn(dbname, coll, secrets)
    res = conn.update_one({'_id': id}, {'$set': content})

    LOG.info('Updated doc - %s - %s - %s', dbname, coll, id)

    return res


def search_mongo(dbname,
                 coll,
                 query,
                 secrets,
                 project=None):
    """
    Run search on MONGO and return results

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param query: (dict) mongo query as dict
    :param secrets: (dict) Result from helpers.get_secrets
    :param project: (dict) mongo projection syntax as dict
    :return: (pymongo.cursor.Cursor) MONGO cursor for iterating over results
    """

    conn = get_coll_conn(dbname, coll, secrets)

    if isinstance(query, dict):
        res = conn.find(query, project)
    if isinstance(query, list):
        if project:
            query.append({'$project': project})
        res = conn.aggregate(query)

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


def auth_user(dbname,
              coll,
              auth_dict,
              token_handler,
              secrets):
    """
    Auth user against coll and return token or None if not authorized

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param auth_dict: (dict) Dict with user details for query
    :param token_handler: (TokenHandler)
    :param secrets: (dict) Result from helpers.get_secrets
    :return: (bool) True if exists \ False if not
    """

    conn = get_coll_conn(dbname, coll, secrets)
    query = build_query('and', kv_pairs=auth_dict)
    res = search_mongo(dbname, coll, query, secrets, EXCLUDE_KEYS_FROM_AUTH_QUERY)
    res = [d for d in res]

    user_token = None

    if len(res) != 0:
        user_info = res[0]
        user_token = token_handler.gen_token(user_info)

    return user_token


def stt_json_to_mongo_frmt(doc,
                           stt_json):
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


def delete_from_mongo(dbname,
                      coll,
                      id,
                      secrets):
    """
    Delete doc from mongo

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param id: (bson.objectid.ObjectId) mongo OID
    :param secrets: (dict) Result from helpers.get_secrets
    :return: (pymongo.results.InsertOneResult) Mongo response
    """

    conn = get_coll_conn(dbname, coll, secrets)
    res = conn.delete_one({'_id': id})

    LOG.info('Deleted doc - %s - %s - %s', dbname, coll, id)

    return res


def org_filter_wrap_and_search(dbname,
                               coll,
                               query,
                               secrets,
                               project=None,
                               user_info=None):
    """
    Wraps a given mongo query with an organization filter and executes the query

    This will only return results that were uploaded by
    users in the same org as the current user

    Returned query should be run with: conn.aggregate(query)
    and not: conn.find(query)

    :param dbname: (str) mongo dbname
    :param coll: (str) mongo collection
    :param query: (dict) mongo query as dict
    :param secrets: (dict) Result from helpers.get_secrets
    :param project: (dict) mongo projection syntax as dict
    :param user_info: (dict) current user info from TokenHandler
    :return: (dict) mongo aggregate query as dicts
    """

    user_info = user_info or {}
    user_id = user_info.get('_id') # (bson.objectid.ObjectId)
    is_admin = user_info.get('admin', False)

    coll_user_id_field = COLL_USER_ID_FIELD_MAP.get(coll)
    if not coll_user_id_field:
        raise Exception('Coll %s Missing in COLL_USER_ID_FIELD_MAP' % coll)

    if not user_id or is_admin:
        wrapped_query = query
    else:
        wrapped_query = [
            {'$match': {'user_id': user_id}},
            {'$project': {'organization_id':1}},
            {'$lookup': {'from': 'users_organizations',
                         'localField': 'organization_id',
                         'foreignField': 'organization_id',
                         'as': 'users'}},
            {'$unwind': '$users'},
            {'$project': {'users.user_id':1}},
            {'$lookup': {'from': coll,
                         'localField': 'users.user_id',
                         'foreignField': coll_user_id_field,
                         'as': 'lookup_res'}},
            {'$unwind': '$lookup_res'},
            {'$project': {'lookup_res':1, '_id':0}},
            {'$replaceRoot': {'newRoot': '$lookup_res'}},
            {'$match': query}
        ]
        # Change coll since it is required for the wrapped query
        # Results will still be returned from original coll
        coll = 'users_organizations'

    return search_mongo(dbname,
                        coll,
                        wrapped_query,
                        secrets,
                        project)
