'''Get directory and file path'''

import os


def get_session_directory(meta_info, output_dir='./outputs'):
    '''Get session directory'''
    directory = output_dir

    user_id = meta_info['userId']
    session_id = meta_info['sessionId']

    if user_id is None:
        directory = os.path.join(directory, 'cache')
    else:
        directory = os.path.join(directory, f'{user_id}')
    if session_id is None:
        directory = os.path.join(directory, 'cache')
    else:
        directory = os.path.join(directory, f'{session_id}')

    return directory


def replace_filename_extension(filename, extension):
    '''Replace filename extension'''
    filename = str(filename)
    return os.path.splitext(filename)[0] + '.' + extension


def replace_filenames_extension(filenames, extension):
    '''Replace filenames extension'''
    return [replace_filename_extension(filename, extension) for filename in filenames]
