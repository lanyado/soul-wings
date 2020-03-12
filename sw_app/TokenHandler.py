import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import inspect
import secrets
from flask import request, redirect
import functools
from datetime import datetime
from config import TOKEN_TIMEOUT_HOURS


class TokenHandler:
    """
    Class for handling tokens of logged in users

    Attributes
    ----------
    tokens : (dict of dicts)
        Dict of recognized tokens
        keys: last_contact (datetime), user_id (str)

    Methods
    -------
    gen_token(user_id)
        Generate token and save to tokens dict
    auth_token(token)
        Auth token and update time if valid
    auth_request(func) - Decorator
        Auth request from user cookie
    """

    def __init__(self,
                 tokens=None):
        """
        Init token handler

        :param tokens: (dict of dicts) Dict of recognized tokens
            keys: last_contact (datetime), user_id (str)
        """

        self.tokens = tokens or {}


    def gen_token(self,
                  user_doc):
        """
        Generate token and save to tokens dict

        :return: (str) token
        """

        user_doc['last_contact'] = datetime.now()

        token = secrets.token_hex()
        self.tokens[token] = user_doc

        return token


    def auth_token(self,
                   token):
        """
        Auth token and update time if valid

        :return: (dict or None) user_doc dict if authorized, None if not
        """

        user_doc = self.tokens.get(token, {})
        token_time = user_doc.get('last_contact', None)

        if not token_time:
            return None

        time_diff = (datetime.now() - token_time).total_seconds()/3600
        if time_diff > TOKEN_TIMEOUT_HOURS:
            self.tokens.pop(token, None)
            return None

        self.tokens[token]['last_contact'] = datetime.now()

        return user_doc


    def auth_request(self,
                     func):
        """
        Decorator: Auth request from user cookie

        Redirects to login or continues to desired server func (page)
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_token = request.cookies.get('soulwings', '')
            user_doc = self.auth_token(user_token)

            if user_doc:
                prms = list(inspect.signature(func).parameters)
                if 'user_doc' in prms:
                    kwargs['user_doc'] = user_doc
                return func(*args, **kwargs)

            else:
                return redirect('/')

        return wrapper
