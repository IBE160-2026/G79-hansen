"""Immutable private uploads and bounded internal readback, never signed URLs."""
import hashlib
from app.adapters.documents import DocumentFailure, SupabaseDocuments

BUCKET = 'studybuddy-sources'


class SupabaseStorage(SupabaseDocuments):
    def upload(self, identity, operation, content, deadline):
        try:
            with self.client(identity, deadline) as client:
                with client.stream('POST', self.settings.supabase_url + '/storage/v1/object/' + BUCKET + '/' + operation['objectKey'],
                        content=content, headers={'Content-Type': operation['mediaType'], 'x-upsert': 'false'}) as response:
                    # Response bodies carry no authority. Do not consume them;
                    # closing the stream bounds even an arbitrarily large body.
                    # Duplicate immutable keys are reconciled, never overwritten.
                    if response.status_code not in (200, 201, 400, 409):
                        raise DocumentFailure()
        except Exception:
            raise DocumentFailure('save_pending') from None

    def verify(self, identity, operation, deadline):
        try:
            with self.client(identity, deadline, verification=True) as client:
                with client.stream('GET', self.settings.supabase_url + '/storage/v1/object/authenticated/' + BUCKET + '/' + operation['objectKey']) as response:
                    if response.status_code != 200:
                        raise DocumentFailure('file_required' if response.status_code == 404 else 'save_pending')
                    total, hash_ = 0, hashlib.sha256()
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > operation['snapshot']['fileSize']:
                            raise DocumentFailure('save_mismatch')
                        hash_.update(chunk)
                    if total != operation['snapshot']['fileSize'] or hash_.hexdigest() != operation['snapshot']['fileHash']:
                        raise DocumentFailure('save_mismatch')
        except DocumentFailure:
            raise
        except Exception:
            raise DocumentFailure() from None

    def delete(self, identity, key, deadline):
        try:
            with self.client(identity, deadline) as client:
                with client.stream('DELETE', self.settings.supabase_url + '/storage/v1/object/' + BUCKET,
                                   json={'prefixes': [key]}) as response:
                    if response.status_code != 200:
                        raise DocumentFailure()
        except Exception:
            raise DocumentFailure() from None
