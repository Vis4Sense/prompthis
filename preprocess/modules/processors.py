processors = {}

def register_processor(name):
    def decorator(cls):
        processors[name] = cls
        return cls
    return decorator
