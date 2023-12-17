import uuid


def form_name_generator():
    name = int(uuid.uuid1())
    return "Form" + str(name)[:4]
