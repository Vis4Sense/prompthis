readers = {}

def register_reader(name):
    def decorator(cls):
        readers[name] = cls
        return cls
    return decorator
