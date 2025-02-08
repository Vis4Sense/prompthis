import json
import requests
import translators.extension_dsl2api as dsl2api
from modules.reader.readers import readers
from modules.logger.base_logger import BaseLogger


class Extension:
    def __init__(self, config):
        self.config = config
        self.url = config["url"]
        self.trigger_time = config["trigger_time"]

    def __str__(self) -> str:
        return str(self.config)

    def __lt__(self, other):
        return self.config["trigger_order"] < other.config["trigger_order"]

    def execute(self):
        print("execute extension")

        input_data = self.get_input()

        payload = {
            "input": input_data,
            "config": self.config
        }

        response = requests.post(url=self.url, json=payload, timeout=10).json()
        output_data = response["output"]
        self.log_output(output_data)

    def get_input(self):
        read_dsl = {
            'metaInfo': self.config['metaInfo'],
            'attributes': self.config['input']
        }
        session_reader = readers['session']
        session_reader = session_reader(read_dsl)
        input_data = session_reader.read()

        return input_data

    def log_output(self, output_data):
        output_api = dsl2api.output_dsl2api(output_data, self.config)
        logger = BaseLogger(**output_api)
        print("logger:", logger)
        logger.write()
