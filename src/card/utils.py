import uuid


def card_name_generator():
    name = int(uuid.uuid1())
    return "Template" + str(name)[:4]
