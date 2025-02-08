import yaml

config_paths = {
    "models": "./models.yaml",
    "extensions": "./extensions.yaml",
}


def read_config(name):
    with open(config_paths[name], "r", encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    return config


def read_configs():
    return read_config("models"), read_config("extensions")
