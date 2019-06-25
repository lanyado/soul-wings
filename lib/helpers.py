"""
This Module contains general helper functions:
file_to_local_uuid_file(f)
    Saves a file object to a local file with a UUID name
"""

import os
import uuid


def file_to_local_uuid_file(f):
    """
    Saves a file object to a local file with a UUID name

    :param f: (werkzeug.datastructures.FileStorage)
    :return: (str) local file path
    """

    file_ext = os.path.splitext(f.filename)[1]
    uuid_path = '{}/working_dir/{}{}'.format(os.getcwd(),
                                             uuid.uuid4(),
                                             file_ext)
    f.save(uuid_path)

    return uuid_path
