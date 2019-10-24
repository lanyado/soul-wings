
import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import re
from lib.mongo import search_mongo, \
                      build_query
from config import TERM_TYPE_MAP, \
                   OPERATOR_MAP, \
                   DEFAULT_CONTEXT_BLOCK_SIZE, \
                   MONGO_DBNAME


class DocMatch:
    """
    """

    def __init__(self,
                 body,
                 search):
        """


        :param body: (dict) mongo doc body as dict
        :param search: (Search) Search obj
        """

        self.body = dict(body)
        self.search = search

        words = self.body.get('words', [])
        self.words = [w['word'] for w in words]
        word_count = len(self.words)

        # List of scores, each idx is the start of a
        # context block and the value of the idx is its score
        self.matches = [[] for idx in range(word_count)]
        self.scores = [0 for idx in range(word_count)]

        self.score_sum = 0


    def run(self):
        """

        :param res:
        """

        self.update_matches()
        self.update_scores(True)
        self.extract_context_blocks()
        self.frmt_cntx_blocks()
        self.frmt_for_html()


    def term_match(self,
                   term):
        """
        Match qouted type terms with the words list

        :param term: (str) term to match
        :set attr: matches (list of lists of dicts)
            idx relates to words list and each list contains dicts of matches
            keys - term (str), score (int)
        """

        def match_phrase(phrase_lst,
                         w_idx):
            """
            Match phrases and score

            Partial matching is supported for first and last
            words of the phrase or if the phrase is only a single word

            :param phrase_lst: (list of str) str for each word in the phrase
            :param w_idx: (int) idx of current word
            """

            match_objs = []

            for t_idx, t in enumerate(phrase_lst):
                w = self.words[w_idx]
                match_obj = {'term': t,
                             'score': 1}

                if t == w:
                    match_obj['score'] = 3
                    match_objs.append(match_obj)
                    w_idx += 1
                    continue

                elif t_idx == 0 and w.endswith(t):
                    match_objs.append(match_obj)
                    w_idx += 1
                    continue

                elif t_idx + 1 == len(phrase_lst) and w.startswith(t):
                    match_objs.append(match_obj)
                    w_idx += 1
                    continue

                elif len(phrase_lst) == 1 and t in w:
                    match_objs.append(match_obj)
                    w_idx += 1
                    continue

                break

            return match_objs


        phrase_lst = term.split()

        for w_idx, w in enumerate(self.words):
            match_objs = match_phrase(phrase_lst, w_idx)

            if len(match_objs) != len(phrase_lst):
                continue

            for m_idx, m in enumerate(match_objs):
                self.matches[w_idx + m_idx].append(m)
                self.score_sum += m['score']


    def update_matches(self):
        """
        Score each word based on the match type and return matched_idxs

        Scoring:
            partial word\phrase match - 1
            full word\phrase match - 3

        :set attr: matches (list of lists of dicts)
            idx relates to words list and each list contains dicts of matches
            keys - term (str), score (int)
        """

        TERM_MATCH_FUNC_MAP = {'single': self.term_match,
                               'qouted': self.term_match}

        for t in self.search.terms:
            TERM_MATCH_FUNC_MAP[t['type']](t['term'])


    def update_scores(self,
                      add_score,
                      m_start=None,
                      m_end=None):
        """
        Update score attr based on matches attr

        :param add_score: (bool) True add score \ False decrease score
        :
        """

        m_start = m_start or 0
        m_end = m_end or len(self.matches)

        for idx, match_lst in \
        enumerate(self.matches[m_start:m_end]):
            idx += m_start
            for m in match_lst:
                m_score = m['score']
                s_start = max(idx - self.search.cbs_half_b, 0)
                s_end = idx + self.search.cbs_half_a

                for i, s in enumerate(self.scores[s_start:s_end]):
                    if add_score:
                        self.scores[s_start + i] += m_score
                    else:
                        self.scores[s_start + i] -= m_score


    def max_score_peak_middle(self,
                              max_score):
        """
        """

        max_score_idx = self.scores.index(max_score)

        counter = 0
        while self.scores[max_score_idx+counter] == max_score:
            if max_score_idx + counter + 1 == len(self.scores):
                break
            counter += 1

        middle = int(counter / 2)
        max_score_idx = max_score_idx + middle

        return max_score_idx


    def frmt_start_time(self,
                          start_time):
        """
        """

        start_time = start_time[:-1]
        start_time = max(float(start_time) - 2, 0)

        return start_time


    def frmt_cntx_blocks(self):
        """
        """

        for b_idx, b in enumerate(self.cntx_blocks):
            b_start = max(b - self.search.cbs_half_b, 0)
            b_end = b + self.search.cbs_half_a
            text = ' '.join(self.words[b_start:b_end])
            long_text = ' '.join(self.words[b_start*2:b_end*2])

            start_time = self.body.get('words')[b_start].get('startTime')
            start_time = self.frmt_start_time(start_time)


            self.cntx_blocks[b_idx] = {'start_time': start_time,
                                       'text': text,
                                       'long_text': long_text}



    def extract_context_blocks(self):
        """
        Extract and order list of context blocks based on score concentration

        :return:
        """

        self.cntx_blocks = []

        max_score = max(self.scores)

        while max_score > 0:
            max_score_idx = self.max_score_peak_middle(max_score)
            self.cntx_blocks.append(max_score_idx)

            m_start = max(max_score_idx - self.search.cbs_half_b, 0)
            m_end = max_score_idx + self.search.cbs_half_a

            self.update_scores(add_score=False,
                               m_start=m_start,
                               m_end=m_end)

            max_score = max(self.scores)


    def frmt_for_html(self):
        """
        """

        result = {}
        user_fields = self.body.get('user_fields', {})

        result['file_name'] = user_fields.get('name', '')
        result['language'] = user_fields.get('lang', '')
        result['context_blocks'] = list(self.cntx_blocks)

        url = 'https://' + \
              self.body.get('s3_bucket', '') + \
              '.s3.amazonaws.com/' + \
              self.body.get('s3_original_key', '')

        result['s3_url'] = url

        result['tags'] = ''
        result['years'] = ''
        result['countries'] = ''
        result['cities'] = ''
        result['camps'] = ''

        self.result = result
