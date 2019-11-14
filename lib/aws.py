"""
This Module contains AWS helper functions:
manage_kwargs(kwargs)
    Add AWS creds to kwargs dict
========================================================================================================================
s3_put_file(local_path, bucket, key, **kwargs)
    Upload file content to provided S3 location
========================================================================================================================
get_s3_url(bucket, key)
    Get S3 url for bucket and key pair
"""

import os
import sys

REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_DIRECTORY)

import boto3
from lib.log import getLog
from proj_secrets import secrets


LOG = getLog('AWS')


def manage_kwargs(kwargs):
    """
    Add AWS creds to kwargs dict

    :param kwargs: (dict)
    :return: (dict) Edited dict
    """

    if not kwargs.get('aws_access_key_id'):
        kwargs['aws_access_key_id'] = secrets.aws_access_key_id

    if not kwargs.get('aws_secret_access_key'):
        kwargs['aws_secret_access_key'] = secrets.aws_secret_access_key

    return kwargs


def s3_put_file(local_path,
                bucket,
                key,
                **kwargs):
    """
    Upload file content to provided S3 location

    :param local_path: (str) path of local file to upload
    :param bucket: (str) bucket name in S3
    :param key: (str) full destination path including file name
    :param kwargs: kwargs for boto3.resource
    """

    kwargs = manage_kwargs(kwargs)
    resource = boto3.resource('s3', **kwargs)

    resource.meta.client.upload_file(local_path,
                                     bucket,
                                     key,
                                     ExtraArgs={'ACL':'public-read'})

    LOG.info('Put to S3 - %s - %s/%s', local_path, bucket, key)


def get_s3_url(bucket,
               key):
    """
    Get S3 url for bucket and key pair

    :param bucket: (str) bucket name in S3
    :param key: (str) full destination path including file name
    :return: (str) S3 url
    """

    return 'https://%s.s3.amazonaws.com/%s' % (bucket, key)
