'''
This module is used to convert the DSL to API.
'''
import os

from utils.filepath import get_session_directory, replace_filenames_extension
from .readers import readers


def dsl2api(dsl):
    '''Translate DSL to API.'''
    # print(dsl)
    meta_info = dsl['metaInfo']
    attributes = dsl['attributes']

    apis = []

    for attribute in attributes:
        api = parse_attribute_api(attribute, meta_info)
        apis.append({
            'attribute': attribute,
            'api': api
        })

    return apis


def parse_attribute_api(attribute, meta_info):
    '''Get API for each attribute.'''
    session_directory = get_session_directory(meta_info)
    session_log = get_session_log(session_directory)

    directory, filenames = get_attribute_filenames(attribute, session_directory, session_log)

    if directory is False:
        return False

    def get_all_files():
        mapping, extension = attribute['fileNaming'].split('-')

        if mapping.split('/')[0] == 'log':
            map_obj = mapping.split('/')[1]
            if map_obj == 'image':
                all_files = parse_session_log(session_log, 'image')
            elif map_obj == 'prompt':
                all_files = parse_session_log(session_log, 'prompt_id')
            elif map_obj == 'setting':
                all_files = parse_session_log(session_log, 'setting')
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

        all_files_transformed = replace_filenames_extension(all_files, extension)
        return all_files, all_files_transformed

    def filter_unprocessed(filter_params):
        name = filter_params['name']
        task = filter_params['task']

        # already processed files
        processed_dir = os.path.join(session_directory, name, task)
        if os.path.exists(processed_dir):
            already_processed = os.listdir(processed_dir)
        else:
            already_processed = []

        # all files
        all_files, all_files_transformed = get_all_files()

        unprocessed_indices = [idx for idx, fn in enumerate(all_files_transformed) \
                               if fn not in already_processed]
        return [all_files[idx] for idx in unprocessed_indices]

    def filter_latest(filenames, is_strict=False):
        _, all_files_transformed = get_all_files()
        sorted_files = [fn for fn in all_files_transformed if fn in filenames]

        if len(sorted_files) == 0:
            return None

        latest_file = sorted_files[-1]
        latest_file_strict = all_files_transformed[-1]

        if is_strict and latest_file != latest_file_strict:
            return False
        return latest_file

    def apply_filter(filter, filenames):
        filter_type = filter['type']
        filter_params = filter['params']
        is_strict = filter['strict'] if 'strict' in filter else False

        if filter_type == 'all':
            return filenames
        if filter_type == 'unprocessed':
            return filter_unprocessed(filter_params)
        if filter_type == 'latest':
            return filter_latest(filenames, is_strict)
        raise NotImplementedError

    filenames = apply_filter(attribute['filter'], filenames)

    if filenames is False:
        print('file not found for attribute:', attribute)
        return False

    if filter == 'latest' or isinstance(filenames, str):
        mode = 'one'
    else:
        mode = 'list'

    return {
        'mode': mode,
        'directory': directory,
        'filenames': filenames,
    }


def get_attribute_filenames(attribute, session_directory, session_log):
    path = attribute['attribute']
    paths = path.split('/')

    directory = ''
    filenames = []

    if paths[0] == 'log':
        if paths[1] == 'image':
            directory = os.path.join(session_directory, 'data')
            filenames = parse_session_log(session_log, 'image')
        elif paths[1] == 'setting':
            directory = os.path.join(session_directory, 'data')
            filenames = parse_session_log(session_log, 'setting')
        elif paths[1] == 'log':
            directory = session_directory
            filenames = 'log.csv'
        else:
            raise NotImplementedError
    else:
        path = os.path.join(session_directory, path)
        if os.path.exists(path):
            directory = path
            filenames = os.listdir(directory)
        else:
            print('cannot find directory:', path)
            return False, False

    return directory, filenames


def parse_session_log(session_log, attribute):
    if attribute == 'image':
        return [fn for item in session_log for fn in item['output_filenames']]
    if attribute == 'prompt_id':
        return [item['prompt_id'] for item in session_log]
    if attribute == 'setting':
        return [item['setting_filename'] for item in session_log]
    if attribute == 'log':
        return 'log.csv'
    raise NotImplementedError


def get_session_log(session_directory):
    '''Get log from session directory.'''
    log_reader = readers['base']
    log_reader = log_reader(mode='one', directory=session_directory, \
                            filenames='log.csv')
    return log_reader.read()
