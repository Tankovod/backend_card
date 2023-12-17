import uuid


def client_name_generator():
    name = int(uuid.uuid1())
    return "Template" + str(name)[:4]
