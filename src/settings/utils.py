import uuid


def generic_public_key():
    pub = str(uuid.uuid4())
    pub2 = str(uuid.uuid4())
    pub3 = str(uuid.uuid4())
    return pub[:5] + pub2[:5] + pub3[:5]