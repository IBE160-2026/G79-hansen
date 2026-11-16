"""Exclusive local server capability setup. Prints only ID and SHA-256 verifier."""
import argparse
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import sys


def initialize(path):
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[1]
    # Refuse an unignored destination before creating anything.
    result = subprocess.run(['git', 'check-ignore', '--quiet', '--', str(path)], cwd=root,
                            capture_output=True)
    if result.returncode != 0:
        raise ValueError('Destination must be ignored by Git.')
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        if os.name == 'nt':
            sid = subprocess.run(['powershell', '-NoProfile', '-Command',
                '[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value'],
                capture_output=True, text=True, check=True).stdout.strip()
            subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r', '*' + sid + ':(F)'],
                           capture_output=True, check=True)
        else:
            os.fchmod(descriptor, 0o600)
        key = secrets.token_hex(32)
        with os.fdopen(descriptor, 'w', encoding='ascii', newline='') as stream:
            descriptor = None
            stream.write(key)
            stream.flush()
            os.fsync(stream.fileno())
        return hashlib.sha256(key.encode('ascii')).hexdigest()
    except BaseException:
        if descriptor is not None:
            os.close(descriptor)
        # On failure the empty/exclusively-created file is retained, never overwritten.
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', default='.save-backend-key')
    parser.add_argument('--key-id', default='save-v1')
    args = parser.parse_args()
    try:
        verifier = initialize(args.path)
    except (OSError, ValueError, subprocess.SubprocessError):
        print('Key setup failed; existing files are never overwritten.', file=sys.stderr)
        return 1
    print('keyId=' + args.key_id)
    print('sha256=' + verifier)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
