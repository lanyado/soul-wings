"""
This Module contains FFMPEG helper functions:
vid_to_flac(path)
    Converts video to mono flac and returns flac path
========================================================================================================================
get_media_length(path)
    Get length of media file in seconds
========================================================================================================================
get_thumbnail(path, seconds)
    Extracts a png thumbnail from a video and returns png path
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import subprocess
from datetime import timedelta
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


def get_media_length(path):
    """
    Get length of media file in seconds

    :param path: (str) local path of file
    :return: (float) file length in seconds
    """

    ffmpeg_call = ('ffprobe -v error -show_entries format=duration '
                   '-of default=noprint_wrappers=1:nokey=1 "{}"').format(path)

    res = subprocess.check_output(ffmpeg_call, shell=True)

    LOG.info('Got Media Length - %s', path)

    return float(res)


def get_thumbnail(path,
                  rel_time):
    """
    Extracts a png thumbnail from a video and returns png path

    :param path: (str) local path of file
    :param rel_time: (float) Fraction of total media time to get thumbnail
    :return: (str) png path
    """

    png_path = os.path.splitext(path)[0] + '.png'

    media_length = get_media_length(path)
    thumbnail_time = str(timedelta(seconds=media_length*rel_time))

    ffmpeg_call = 'ffmpeg -i "{}" -ss {} -vframes 1 "{}"'.format(path,
                                                                 thumbnail_time,
                                                                 png_path)

    res = subprocess.check_output(ffmpeg_call, shell=True)

    LOG.info('Got thumbnail - %s', path)

    return png_path
