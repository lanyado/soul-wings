"""
This Module contains FFMPEG helper functions:
vid_to_flac(path)
    Converts video to mono flac and returns flac path
========================================================================================================================
get_thumbnail(path, seconds)
    Extracts a png thumbnail from a video and returns png path
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

    if os.path.splitext(path)[1] == '.flac':
        flac_path = os.path.splitext(path)[0] + '_1.flac'
    else:
        flac_path = os.path.splitext(path)[0] + '.flac'

    if os.path.isfile(flac_path):
        os.remove(flac_path)

    ffmpeg_call = 'ffmpeg -i "{}" -f flac -ac 1 -vn "{}"'.format(path,
                                                                 flac_path)
    subprocess.check_output(ffmpeg_call, shell=True)

    LOG.info('Converted file - %s', path)

    return flac_path


def get_thumbnail(path,
                  seconds):
    """
    Extracts a png thumbnail from a video and returns png path

    :param path: (str) local path of file
    :param seconds: (int) time in video for thumbnail
    :return: (str) png path
    """

    png_path = os.path.splitext(path)[0] + '.png'

    ffmpeg_call = 'ffmpeg -i "{}" -ss 00:00:{}.000 -vframes 1 "{}"'.format(path,
                                                                           seconds,
                                                                           png_path)
    subprocess.check_output(ffmpeg_call, shell=True)

    LOG.info('Got thumbnail - %s', path)

    return png_path
