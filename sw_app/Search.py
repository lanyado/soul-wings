
import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import re
from DocMatch import DocMatch
from lib.mongo import search_mongo, \
                      build_query
from config import TERM_TYPE_MAP, \
                   OPERATOR_MAP, \
                   DEFAULT_CONTEXT_BLOCK_SIZE, \
                   MONGO_DBNAME, \
                   TRANSCRIPTS_COLL, \
                   DEFAULT_OPERATOR


class Search:
    """
    """

    def __init__(self,
                 search_string,
                 operator=DEFAULT_OPERATOR,
                 cntx_block_size=DEFAULT_CONTEXT_BLOCK_SIZE,
                 mongo_dbname=MONGO_DBNAME,
                 mongo_coll=TRANSCRIPTS_COLL):
        """


        :param search_string: (str) Search string
        :param operator: (str) Operator that will act in the query (and \ or)
        :param cntx_block_size: (int) Size of context block
        """

        self.ss = search_string
        self.operator = operator
        self.set_cntx_block_attrs(cntx_block_size)
        self.mongo_dbname = mongo_dbname
        self.mongo_coll = mongo_coll
        self.resp_json = {'search_string': search_string,
                          'operator': operator}


    def run(self):
        """
        """

        self.search_string_to_terms()
        query = build_query(self.operator, terms=self.terms)
        res = search_mongo(self.mongo_dbname, self.mongo_coll, query)
        self.frmt_mongo_res(res)


    def set_cntx_block_attrs(self,
                             cntx_block_size):
        """
        Check that block size is an odd number
        and set half_b\a attrs

        :param cntx_block_size: (int) Size of context block
        :set attr: cntx_block_size (int) Size of context block
                   half_b (int) Half cntx block for before match
                   half_a (int) Half cntx block for after match
        """

        self.cntx_block_size = cntx_block_size

        if self.cntx_block_size % 2 == 0:
            self.cntx_block_size += 1

        self.cbs_half_b = int(self.cntx_block_size / 2)
        self.cbs_half_a = self.cbs_half_b + 1


    def search_string_to_terms(self):
        """
        Converts a search string to a list of terms

        :set attr: terms (list of dicts) dict per term
            keys - term (str), type (str)
        """

        terms = []
        # Format utf8 qoutes
        self.ss = self.ss.replace('״', '"')

        qoute_terms = re.findall(r'"(.*?)"', self.ss)

        for qt in qoute_terms:
            wrapped_qt = '"' + qt + '"'
            self.ss = self.ss.replace(wrapped_qt, '')
            terms.append({'term': qt, 'type': 'qouted'})

        single_terms = self.ss.split(' ')
        single_terms = [t for t in single_terms if t]

        for st in single_terms:
            terms.append({'term': st, 'type': 'single'})

        self.terms = terms
        self.resp_json['terms'] = terms


    def frmt_mongo_res(self,
                         res):
        """


        :param res: (pymongo.cursor.Cursor) Mongo query result
        :set attr: resp_json (dict) response json for frontend
        """

        results = []

        for doc in res:
            doc = DocMatch(doc, self)
            doc.run()
            results.append(doc)

        results = sorted(results,
                         key=lambda d: d.score_sum,
                         reverse=True)

        results = [d.result for d in results]

        self.resp_json['results'] = results
