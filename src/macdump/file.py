from macdump.log import status
from macdump.shared import dump


def dump_hash_from(data):
    authentication_hint = extract_authentication_hint_from(data)
    if authentication_hint:
        status(f"Authentication hint: {authentication_hint}")

    user = extract_username_from(data) or "UNKNOWN_USER"
    shadow_hash_data = extract_shadow_hash_data_from(data)
    dump(user, shadow_hash_data)


# returns the line after "dsAttrTypeNative:ShadowHashData:"
def extract_shadow_hash_data_from(path):
    shadow_data = extract_line_after_from(
        path, target_line="dsAttrTypeNative:ShadowHashData:"
    )
    if not shadow_data:
        raise Exception(f"Shadow hash data not found in {path}")

    return shadow_data


# returns the line after "dsAttrTypeNative:ShadowHashData:"
def extract_username_from(data):
    for line in data.split("\n"):
        line = line.strip()
        if line.startswith("RecordName:"):
            return line.split(":")[1].strip()
    return ""


# returns the line after "AuthenticationHint:"
def extract_authentication_hint_from(data):
    return extract_line_after_from(data, "AuthenticationHint:")


def extract_line_after_from(data, target_line):
    return_next = False
    for line in data.split("\n"):
        line = line.strip()
        if return_next:
            return line

        if line == target_line:
            return_next = True

    return ""
