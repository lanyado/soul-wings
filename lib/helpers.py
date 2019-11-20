"""
This Module contains general helper functions:
file_to_local_uuid_file(f)
    Saves a file object to a local file with a UUID name
========================================================================================================================
clean_working_dir(working_dir)
    Delete all files from working dir except .gitignore
========================================================================================================================
get_best_alt(alts)
    Return words list from alternative with highest confidence
========================================================================================================================
lower_all_vals(d)
    Lowers all string \ unicode values in a dict
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import uuid
import glob
from config import WORKING_DIR


def file_to_local_uuid_file(f):
    """
    Saves a file object to a local file with a UUID name

    :param f: (werkzeug.datastructures.FileStorage)
    :return: (str) local file path
    """

    file_ext = os.path.splitext(f.filename)[1]
    uuid_path = '{}/{}{}'.format(WORKING_DIR,
                                 uuid.uuid4(),
                                 file_ext)
    f.save(uuid_path)

    return uuid_path


def clean_working_dir(working_dir=WORKING_DIR):
    """
    Delete all files from working dir except .gitignore

    :param working_dir: (str) path to clean
    :return: (list of str) paths of files deleted
    """

    files = glob.glob(working_dir + '/*')
    for f in files:
        os.remove(f)

    return files


def get_best_alt(alts):
    """
    Return words list from alternative with highest confidence

    :param alts: (list of dicts) alternatives from STT response
    :return: (list of dicts) Best alternative, dict per word
        keys - word, startTime, endTime
    """

    max_conf = 0
    best_alt = None

    for alt in alts:
        conf = alt.get('confidence', 0.1)
        if conf > max_conf:
            max_conf = conf
            best_alt = alt.get('words', [])

    return best_alt


def lower_all_vals(d):
    """
    Lowers all string \ unicode values in a dict

    :param d: (dict)
    :return: (dict) Formatted dict
    """

    for k, v in d.items():
        if isinstance(v, str):
            d[k] = v.lower()

    return d
