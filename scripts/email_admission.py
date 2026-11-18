"""Initialize new, dedicated email admission state offline; never reset it."""

import argparse

from app.adapters.auth import AuthFailure
from app.services.email_admission import EmailAdmission


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('init',))
    parser.add_argument('path')
    args = parser.parse_args()
    try:
        EmailAdmission.initialize(args.path)
    except AuthFailure:
        parser.exit(1, 'Email admission unavailable; existing state is never reset.\n')
    print('Email admission initialized. Fixed rolling-hour limits: 2 global, 1 per recipient.')


if __name__ == '__main__':
    main()
