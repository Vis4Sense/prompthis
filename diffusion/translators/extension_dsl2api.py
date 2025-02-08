import os
import json

from modules.reader.readers import readers
from modules.reader.dsl2api import dsl2api as read_dsl2api
from utils.filepath import get_session_directory


def inputs_dsl2api(dsl):
    read_dsl = {
        'metaInfo': dsl['metaInfo'],
        'attributes': dsl['input']
    }
    return read_dsl2api(read_dsl)


def input_dsl2api(input_dsl, dsl):
    print("translating input dsl to api...")

    attribute = input_dsl["attribute"]
    filter = input_dsl["filter"]

    thread_directory = get_thread_directory(dsl["data"])

    thead_log = get_thread_log(thread_directory)

    def get_all_image_filenames():
        return [fn for item in thead_log for fn in item["output_filenames"]]

    def get_all_prompt_ids():
        return [item["prompt_id"] for item in thead_log]

    def filenames_of_attribute(attribute):
        attributes = attribute.split("/")
        directory = os.path.join(thread_directory, attribute)
        filenames = []
        if attributes[0] == "log":
            if attributes[1] == "image":
                directory = os.path.join(thread_directory, "data")
                filenames = get_all_image_filenames()
            elif attributes[1] == "log":
                directory = thread_directory
                filenames = "log.csv"
            else:
                raise NotImplementedError
        else:
            if os.path.exists(directory):
                filenames = os.listdir(directory)
        return directory, filenames

    def apply_unprocessed_filter(filenames):
        _, _, suffix = dsl["output"].split("-")

        reference_filenames = ["".join(fn.split(".")[:-1]) for fn in filenames]
        reference_filenames = [f"{fn}.{suffix}" for fn in reference_filenames]

        output_directory = os.path.join(thread_directory, dsl["name"], dsl["task"])
        if os.path.exists(output_directory):
            output_filenames = os.listdir(output_directory)
        else:
            output_filenames = []

        unprocessed_indices = [idx for idx, fn in enumerate(reference_filenames) \
                                if fn not in output_filenames]

        return [filenames[idx] for idx in unprocessed_indices]

    def apply_latest_filter(filenames):
        _, mapping, suffix = dsl["output"].split("-")

        if mapping.split("/")[0] == "log":
            map_obj = mapping.split("/")[1]
            if map_obj == "image":
                reference_filenames = get_all_image_filenames()
                reference_filenames = ["".join(fn.split(".")[:-1]) \
                                        for fn in reference_filenames]
            elif map_obj == "prompt":
                reference_filenames = get_all_prompt_ids()
            else:
                raise NotImplementedError
            reference_filenames = [f"{fn}.{suffix}" for fn in reference_filenames]
        else:
            raise NotImplementedError

        sorted_filenames = [fn for fn in reference_filenames if fn in filenames]
        if len(sorted_filenames) == 0:
            return None
        return sorted_filenames[-1]

    def apply_filter(filter, filenames):
        if filter == "all":
            return filenames
        if filter == "unprocessed":
            return apply_unprocessed_filter(filenames)
        if filter == "latest":
            return apply_latest_filter(filenames)
        raise NotImplementedError

    dir, fns = filenames_of_attribute(attribute)
    fns = apply_filter(filter, fns)

    if filter == "latest" or isinstance(fns, str):
        mode = "one"
    else:
        mode = "list"

    return {
        "mode": mode,
        "directory": dir,
        "filenames": fns,
        "dsl": input_dsl
    }


def output_dsl2api(output_data, config):
    files = []

    thread_directory = get_session_directory(config["metaInfo"])
    directory = os.path.join(thread_directory, config["name"], config["task"])

    if not os.path.exists(directory):
        os.makedirs(directory)

    target, mapping, suffix = config["output"].split("-")

    if target == "map":
        mode = "list"
        for item in output_data:
            filename, _ = os.path.splitext(item["filename"])
            filename = f"{filename}.{suffix}"
            files.append({
                "filename": filename,
                "data": item["data"]
            })
    elif target == "latest":
        mode = "one"

        if mapping.split("/")[0] == "log":
            map_obj = mapping.split("/")[1]
            if map_obj == "prompt":
                prompt_ids = get_thread_prompt_ids(thread_directory)
                filename = f"{prompt_ids[-1]}.{suffix}"
                files = {
                    "filename": filename,
                    "data": output_data
                }
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

    return {
        "mode": mode,
        "directory": directory,
        "files": files,
        "dsl": config
    }


def get_thread_prompt_ids(thread_directory):
    thead_log = get_thread_log(thread_directory)
    return [item["prompt_id"] for item in thead_log]


def get_thread_log(directory):
    log_reader = readers["base"]
    log_reader = log_reader(mode="one", directory=directory, \
                             filenames="log.csv")
    log = log_reader.read()
    return log


def get_thread_directory(data):
    log_dir = "./outputs"
    directory = ""

    user_id = data["user_id"]
    thread_id = data["thread_id"]

    if user_id is None:
        directory = os.path.join(log_dir, "cache")
    elif thread_id is None:
        directory = os.path.join(log_dir, f"{user_id}", "cache")
    else:
        directory = os.path.join(log_dir, f"{user_id}", f"{thread_id}")

    return directory
