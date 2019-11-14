import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

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
                  user_id):
        """
        Generate token and save to tokens dict

        :return: (str) token
        """

        token = secrets.token_hex()
        self.tokens[token] = {'last_contact': datetime.now(),
                              'user_id': user_id}

        return token


    def auth_token(self,
                   token):
        """
        Auth token and update time if valid

        :return: (bool) True if valid, False if not
        """

        token_dict = self.tokens.get(token, {})
        token_time = token_dict.get('last_contact', None)

        if not token_time:
            return False

        time_diff = (datetime.now() - token_time).total_seconds()/3600
        if time_diff > TOKEN_TIMEOUT_HOURS:
            self.tokens.pop(token, None)
            return False

        self.tokens[token]['last_contact'] = datetime.now()

        return True


    def auth_request(self,
                     func):
        """
        Decorator: Auth request from user cookie

        Redirects to login or continues to desired server func (page)
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_token = request.cookies.get('soulwings', '')

            if not self.auth_token(user_token):
                return redirect('/')
            else:
                return func(*args, **kwargs)

        return wrapper
