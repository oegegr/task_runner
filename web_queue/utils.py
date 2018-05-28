import json


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

def json_validation(request):
    errors = []
    schema = {
        ""
    }
    json = request.get_json()

def to_json(data):
    return json.dumps(data)
