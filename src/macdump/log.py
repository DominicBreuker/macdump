verbose = True


def set_quiet():
    global verbose
    verbose = False


def status(msg: str):
    if verbose:
        print(f"[+] {msg}")


def error(msg: str):
    print(f"[!] {msg}")
