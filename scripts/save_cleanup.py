"""Expire owner staging and retry registered cleanup using a fresh user token."""
import argparse
import asyncio
from getpass import getpass
import time
from uuid import UUID
from app.adapters.auth import SupabaseAuth, Identity
from app.adapters.documents import SupabaseDocuments
from app.adapters.storage import SupabaseStorage
from app.config import Settings
from app.services.documents import Documents, SaveAdmission


async def cleanup(settings, identity):
    service = Documents(SupabaseDocuments(settings), SupabaseStorage(settings), None, SaveAdmission())
    complete, pending, cursor = 0, 0, None
    while True:
        page = await service.rpc(identity, 'pending', {'schemaVersion': '1.0', 'cursor': cursor}, time.monotonic()+60)
        for operation in page['operations']:
            if operation.get('cleanupOnly') or operation['status'] in ('expired', 'cancelled', 'conflict'):
                result = await service.cleanup(identity, operation['operationId'], time.monotonic()+60)
                if result['status'] == 'cleanup_complete':
                    complete += 1
                else:
                    pending += 1
        cursor = page.get('nextCursor')
        if not cursor:
            break
    return complete, pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    settings = Settings.from_env()
    try:
        settings.save_backend_key()
        token = getpass('Fresh same-owner user JWT (hidden): ')
        with SupabaseAuth(settings).client() as auth:
            user = auth.get_user(token).user
        if not user or not user.email_confirmed_at:
            raise ValueError()
        identity = Identity(str(UUID(user.id)), user.email, token, '', time.time()+60)
        complete, pending = asyncio.run(cleanup(settings, identity))
        print(f'{complete} object-free operations complete; {pending} registered file operations remain cleanup pending.')
        return 0
    except Exception:
        print('Cleanup was not confirmed. Recovery records are retained.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
