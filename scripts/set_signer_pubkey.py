import re
from pathlib import Path
from argparse import ArgumentParser

parser = ArgumentParser(
    prog="metadata", description="Change SIGNER_PUBKEY in src/krux/metadata.py"
)

parser.add_argument("-P", "--pubkey")
args = parser.parse_args()

PATH = Path("src/krux/metadata.py")

s = PATH.read_text(encoding="utf-8")
s2 = re.sub(
    r'^(\s*SIGNER_PUBKEY\s*=\s*)"[^"]*"',
    r'\1"' + args.pubkey + '"',
    s,
    flags=re.M,
)
PATH.write_text(s2, encoding="utf-8")
