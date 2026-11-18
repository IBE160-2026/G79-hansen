"""Immutable private uploads and bounded internal readback, never signed URLs."""
import hashlib
import json
from urllib.parse import quote
from botocore.auth import S3SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
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
        self.read(identity, {**operation.get('snapshot', {}), 'objectKey': operation['objectKey']}, deadline, verification=True)

    def download(self, identity, descriptor, deadline):
        return self.read(identity, descriptor, deadline)

    def read(self, identity, descriptor, deadline, *, verification=False):
        try:
            # Authenticated REST downloads cache by JWT, without our gate or
            # lifecycle marker. S3 session-token reads re-evaluate RLS per call.
            region = self.settings.supabase_s3_region
            key_id = self.settings.supabase_s3_key_id
            anon_key = self.settings.supabase_s3_anon_key
            if not region or not key_id or not anon_key:
                raise DocumentFailure('save_unavailable')
            url = (self.settings.supabase_url + '/storage/v1/s3/' + BUCKET + '/'
                   + quote(descriptor['objectKey'], safe='/'))
            headers = {'x-studybuddy-backend': self.settings.save_backend_key()}
            if verification:
                headers['x-studybuddy-operation'] = 'verify'
            signed = AWSRequest(method='GET', url=url, headers=headers)
            S3SigV4Auth(Credentials(key_id, anon_key, identity.access_token), 's3', region).add_auth(signed)
            with self.client(identity, deadline, verification=verification) as client:
                with client.stream('GET', url, headers=dict(signed.headers)) as response:
                    if response.status_code != 200:
                        raise DocumentFailure('file_required' if response.status_code == 404 else 'save_pending')
                    expected = descriptor['fileSize']
                    if not isinstance(expected, int) or not 0 <= expected <= 10 * 1024 * 1024:
                        raise DocumentFailure('save_mismatch')
                    content, total, hash_ = bytearray(), 0, hashlib.sha256()
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > expected:
                            raise DocumentFailure('save_mismatch')
                        hash_.update(chunk)
                        if not verification:
                            content.extend(chunk)
                    if total != expected or hash_.hexdigest() != descriptor['fileHash']:
                        raise DocumentFailure('save_mismatch')
                    return bytes(content)
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
                    raw=bytearray()
                    for chunk in response.iter_bytes():
                        if len(raw)+len(chunk)>128*1024: raise DocumentFailure()
                        raw.extend(chunk)
                    removed=json.loads(raw)
                    # A 200/empty list can mean RLS hid the object. The
                    # provider must positively name this exact removed key.
                    return isinstance(removed,list) and len(removed)==1 and isinstance(removed[0],dict) and removed[0].get('name')==key and removed[0].get('bucket_id',BUCKET)==BUCKET
        except Exception:
            raise DocumentFailure() from None

    def absent(self, identity, key, deadline):
        """Fresh S3 check after DB-fenced, settled upload attempts.

        Supabase's S3 facade can return 404 from its metadata lookup even
        while an orphaned physical blob remains. This check is used only
        alongside the exact positive Storage removal receipt AND all settled
        durable upload intents. Alone it cannot certify physical removal.
        The cleanup-only header grants no ordinary file-read authority.
        """
        try:
            if not self.settings.supabase_s3_region or not self.settings.supabase_s3_key_id or not self.settings.supabase_s3_anon_key:
                raise DocumentFailure('delete_pending')
            url = self.settings.supabase_url + '/storage/v1/s3/' + BUCKET + '/' + quote(key, safe='/')
            signed = AWSRequest(method='GET', url=url, headers={
                'x-studybuddy-backend': self.settings.save_backend_key(), 'x-studybuddy-operation': 'cleanup'})
            S3SigV4Auth(Credentials(self.settings.supabase_s3_key_id, self.settings.supabase_s3_anon_key,
                                   identity.access_token), 's3', self.settings.supabase_s3_region).add_auth(signed)
            with self.client(identity, deadline) as client:
                with client.stream('GET', url, headers=dict(signed.headers)) as response:
                    if response.status_code not in (200, 404):
                        raise DocumentFailure('delete_pending')
                    return response.status_code == 404
        except DocumentFailure:
            raise
        except Exception:
            raise DocumentFailure('delete_pending') from None
