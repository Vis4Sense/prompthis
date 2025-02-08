class BaseProcessor:
    def __init__(self, input_data, config, **kwargs) -> None:
        self.input_data = input_data
        self.config = config

    def process(self):
        pass
