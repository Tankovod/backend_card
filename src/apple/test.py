import os


def test(cabinet_id):
    path_client = str(os.getcwd() + f"""/apple/client/{cabinet_id}/certs""")
    pass_path = os.path.join(path_client, "passphrase.key")
    print(pass_path)
    with open(pass_path, "w+") as file:
        file.write("PASSPHRASE")
        file.close()
