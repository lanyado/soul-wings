"""
This Module contains FFMPEG helper functions:
vid_to_flac(path)
    Converts video to mono flac and returns flac path
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import subprocess
from lib.log import getLog


LOG = getLog('FFMPEG')


def vid_to_flac(path):
    """
    Converts video to mono flac and returns flac path

    :param path: (str) local path of file
    :return: (str) converted flac path
    """

    flac_path = os.path.splitext(path)[0] + '.flac'
    if os.path.isfile(flac_path):
        os.remove(flac_path)

    ffmpeg_call = 'ffmpeg -i "{}" -f flac -ac 1 -vn "{}"'.format(path, flac_path)
    subprocess.call(ffmpeg_call, shell=True)

    LOG.info('Converted file - %s', path)

    return flac_path
