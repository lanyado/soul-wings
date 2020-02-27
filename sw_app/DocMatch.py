import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

from lib.aws import get_s3_url
from config import ENRICHMENT_TYPES


class DocMatch:
    """
    Class for matching search terms against a
    mentioned doc from the mongo result set

    Attributes
    ----------
    score_sum : (int)
        Sum of scores from all matched terms
    result : (dict)
        result of matching process
        keys: tags (str), file_name (str)
              language (str), context_blocks (list of dicts)
              s3_url (str), key per enrichment type

    Methods
    -------
    run()
        Run match process and save result to self.result
    """

    def __init__(self,
                 body,
                 search):
        """
        Init DocMatch

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
        self.scores = [0 for idx in range(word_count)]
        self.matches = [[] for idx in range(word_count)]

        self.score_sum = 0


    def run(self):
        """
        Run match process and save result to self.result
        """

        self._update_matches()
        self._update_scores(True)
        self._extract_context_blocks()
        self._frmt_cntx_blocks()
        self._frmt_for_html()


    def _match_phrase(self,
                      phrase_lst,
                      w_idx):
        """
        Match phrases and return list of matched terms and scores

        Partial matching is supported for first and last
        words of the phrase or if the phrase is only a single word

        Scoring:
            partial word\phrase match - 1
            full word\phrase match - 3

        :param phrase_lst: (list of str) str for each word in the phrase
        :param w_idx: (int) idx of current word
        :return: (list of dicts) list of matched terms and scores
            keys: term (str), score (int)
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


    def _term_match(self,
                    term):
        """
        Match term and update matches attr

        :param term: (str) term to match
        :update attr: matches (list of lists of dicts)
                      score_sum (int)
        """

        phrase_lst = term.split()

        for w_idx, w in enumerate(self.words):
            match_objs = self._match_phrase(phrase_lst, w_idx)

            if len(match_objs) != len(phrase_lst):
                continue

            for m_idx, m in enumerate(match_objs):
                self.matches[w_idx + m_idx].append(m)
                self.score_sum += m['score']


    def _update_matches(self):
        """
        Update scoring and matches for each term based on the term type
        """

        TERM_MATCH_FUNC_MAP = {'single': self._term_match,
                               'qouted': self._term_match}

        for t in self.search.terms:
            TERM_MATCH_FUNC_MAP[t['type']](t['term'])


    def _update_scores(self,
                       add_score,
                       m_start=None,
                       m_end=None):
        """
        Update scores attr based on matches attr

        :param add_score: (bool) True add score \ False decrease score
        :param m_start: (int) matches idx start, update idx if >= this idx
        :param m_end: (int) matches idx end, update idx if < this idx
        :update attr: scores (list of ints)
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


    def _max_score_peak_middle(self):
        """
        Find middle of current max score

        Needed in order to find the best place to
        display the context block

        Example: scores [0,0,2,2,5,5,5,2,2,0,0]
                                   ^
        This idx will be returned since it is the best
        place to be the middle of the context block

        :return: (int) Middle of current max score
        """

        max_score = max(self.scores)
        max_score_idx = self.scores.index(max_score)

        counter = 0
        while self.scores[max_score_idx+counter] == max_score:
            if max_score_idx + counter + 1 == len(self.scores):
                break
            counter += 1

        middle = int(counter / 2)
        max_score_idx = max_score_idx + middle

        return max_score_idx


    def _frmt_start_time(self,
                         start_time):
        """
        Format start_time for frontend

        :param start_time: (str) startTime from word dict in words list
        :return: (float) formatted start_time
        """

        start_time = start_time[:-1]
        start_time = max(float(start_time) - 2, 0.0)

        return start_time


    def _extract_context_blocks(self):
        """
        Extract and order list of context blocks based on score concentration

        :set attr: cntx_blocks (list of ints) idx of middle of context block
        """

        self.cntx_blocks = []

        while max(self.scores) > 0:
            max_score_idx = self._max_score_peak_middle()
            self.cntx_blocks.append(max_score_idx)

            m_start = max(max_score_idx - self.search.cbs_half_b, 0)
            m_end = max_score_idx + self.search.cbs_half_a

            self._update_scores(add_score=False,
                                m_start=m_start,
                                m_end=m_end)


    def _frmt_cntx_blocks(self):
        """
        Format context blocks for frontend

        :update attr: cntx_blocks (list of dicts) dict for each
            context block ordered by descending score
            keys: start_time (float), text (str), long_text (str)
        """

        for b_idx, b in enumerate(self.cntx_blocks):
            b_start = max(b - self.search.cbs_half_b, 0)
            b_end = b + self.search.cbs_half_a
            text = ' '.join(self.words[b_start:b_end])
            long_text = ' '.join(self.words[b_start*2:b_end*2])

            start_time = self.body.get('words')[b_start].get('startTime')
            start_time = self._frmt_start_time(start_time)

            self.cntx_blocks[b_idx] = {'start_time': start_time,
                                       'text': text,
                                       'long_text': long_text}

    def _frmt_enrichments(self,
                          result):
       """
       Format enrichments for html

       String that represents a list of strings
       of each enrichment type

       :param result: (dict) result for html
       :return: (dict) result for html with enrichment keys
       """

       res_enrichments = self.body.get('enrichments', [])

       for t in ENRICHMENT_TYPES:
           vals = []
           for e in res_enrichments:
               if e['type'] == t:
                   vals.append(e['value'])

           result[t] = ' ,'.join(vals)

       return result


    def _frmt_for_html(self):
        """
        Format result for frontend

        :set attr: result (dict) Result of the search for this doc
        """

        result = {}
        user_fields = self.body.get('user_fields', {})

        result['tags'] = ' ,'.join(user_fields.get('tags', []))
        result['file_name'] = user_fields.get('file_name', '')
        result['language'] = user_fields.get('language', '')
        result['context_blocks'] = list(self.cntx_blocks)

        s3_bucket = self.body.get('s3_bucket', '')
        s3_original_key = self.body.get('s3_original_key', '')
        result['s3_url'] = get_s3_url(s3_bucket, s3_original_key)

        self.result = self._frmt_enrichments(result)
