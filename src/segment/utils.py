import uuid


def segment_name_generator():
    name = int(uuid.uuid1())
    return "Segment" + str(name)[:4]