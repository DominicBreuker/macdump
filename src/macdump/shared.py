import string
import plistlib


def dump(user, shadow_hash_data):
    props = to_apple_property_list(shadow_hash_data)
    hash_data = props["SALTED-SHA512-PBKDF2"]

    hashcat_hash = get_hash_pbkdf2_sha512(
        hash_data["entropy"], hash_data["salt"], hash_data["iterations"]
    )
    print(f"{user}:{hashcat_hash}")


def to_apple_property_list(shadow_data):
    clean_hex = "".join([c for c in shadow_data.lower() if c in string.hexdigits])
    data = bytes.fromhex(clean_hex)
    return plistlib.loads(data)


def get_hash_pbkdf2_sha512(entropy, salt, iterations):
    return f"$ml${iterations}${salt.hex()}${entropy.hex()}"
