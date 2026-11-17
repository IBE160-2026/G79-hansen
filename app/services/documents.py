"""Explicit immutable admission and same-owner durable recovery; no model access."""
import hashlib
import time
from threading import RLock
from anyio import CapacityLimiter, to_thread
from app.adapters.documents import DocumentFailure
from app.contracts.documents import snapshot, snapshot_digest
from app.services.extraction import decode_file, ExtractionFailure


class SaveAdmission:
    def __init__(self):
        self.sessions, self.tasks = set(), set()
        self.lock = RLock()
        self.limiter = CapacityLimiter(2)

    def acquire(self, session_id):
        with self.lock:
            if session_id in self.sessions or len(self.sessions) >= 2:
                raise DocumentFailure('save_capacity')
            self.sessions.add(session_id)

    def release(self, session_id):
        with self.lock:
            self.sessions.discard(session_id)


class Documents:
    def __init__(self, repository, storage, workspaces, admission):
        self.repository, self.storage, self.workspaces, self.admission = repository, storage, workspaces, admission

    async def io(self, fn, *args):
        return await to_thread.run_sync(fn, *args, limiter=self.admission.limiter)

    async def rpc(self, identity, action, payload, deadline):
        return await self.io(self.repository.call, identity, action, payload, deadline)

    async def download(self, identity, submitted, deadline):
        payload = submitted.model_dump(mode='json', by_alias=True)
        try:
            descriptor = await self.rpc(identity, 'file', payload, deadline)
            content = await self.io(self.storage.download, identity, descriptor, deadline)
            # Never return a blob whose current ready generation changed while
            # S3 was being read. Session authority is checked by the API as well.
            if await self.rpc(identity, 'file', payload, deadline) != descriptor:
                raise DocumentFailure('file_unavailable')
            return content, descriptor
        except DocumentFailure as failure:
            raise DocumentFailure('document_unknown' if failure.code in {'save_unknown', 'document_unknown'} else 'file_unavailable') from None

    @staticmethod
    def file(encoded):
        if encoded is None:
            return None
        try:
            return decode_file(encoded)
        except ExtractionFailure:
            raise DocumentFailure('save_mismatch') from None

    async def save(self, session_id, session, submitted, deadline):
        identity = session.identity
        content = self.file(submitted.content_base64)
        file_hash = hashlib.sha256(content).hexdigest() if content is not None else None
        try:
            frozen = snapshot(submitted, identity.owner_id, file_hash, len(content) if content is not None else None)
        except ValueError:
            raise DocumentFailure('save_mismatch') from None
        digest = snapshot_digest(frozen)
        payload = {'operationId': submitted.operation_id, 'digest': digest}
        # Known operations are handled before any process-local proof/revision checks.
        known = await self.rpc(identity, 'get', payload, deadline)
        if known.get('operation'):
            operation = known['operation']
            if operation['digest'] != digest:
                raise DocumentFailure('save_mismatch')
        else:
            if submitted.acceptance.kind != 'paste' and content is None:
                raise DocumentFailure('file_required')
            async with self.workspaces.admit_save(session_id, session, submitted.receipt, submitted.acceptance, submitted.bundle) as claims:
                if claims['fileHash'] != file_hash:
                    raise DocumentFailure('save_mismatch')
                def dispatch():
                    self.workspaces.registry.live_session(session_id, session)
                    return self.repository.call(identity, 'admit', {**payload, 'snapshot': frozen}, deadline)
                operation = (await self.io(dispatch))['operation']
        return await self.finish(identity, operation, content, deadline)

    async def retry(self, identity, submitted, deadline):
        known = await self.rpc(identity, 'get', {'operationId': submitted.operation_id}, deadline)
        operation = known.get('operation')
        if not operation:
            raise DocumentFailure('save_unknown')
        if operation['digest'] != submitted.digest:
            raise DocumentFailure('save_mismatch')
        return await self.finish(identity, operation, self.file(submitted.content_base64), deadline)

    async def finish(self, identity, operation, content, deadline):
        payload = {'operationId': operation['operationId'], 'digest': operation['digest']}
        # Ready staging is erased, but immutable file identity is retained in
        # the internal operation projection. Omitted bytes still permit replay.
        if content is not None and (operation.get('fileHash') is None or
                len(content) != operation.get('fileSize') or
                hashlib.sha256(content).hexdigest() != operation['fileHash']):
            raise DocumentFailure('save_mismatch')
        if operation['status'] == 'ready':
            return operation['outcome']
        if operation['status'] == 'expired':
            raise DocumentFailure('save_expired')
        if operation['status'] != 'pending':
            raise DocumentFailure('save_conflict')
        if operation.get('objectKey'):
            if content is not None:
                await self.rpc(identity, 'attempt', payload, deadline)
                await self.io(self.storage.upload, identity, operation, content, deadline)
            await self.io(self.storage.verify, identity, operation, deadline)
            await self.rpc(identity, 'verified', payload, deadline)
        result = await self.rpc(identity, 'commit', payload, deadline)
        # Ready is independent of cleanup. Unknown provider writes stay registered.
        return result

    async def cleanup(self, identity, operation_id, deadline):
        fenced = await self.rpc(identity, 'cancel', {'operationId': operation_id}, deadline)
        # The DB fence disallows future metadata finalization. Physical-blob
        # quiescence is a separate provider acceptance gate; retain all records.
        for key in fenced.get('cleanupKeys', []):
            await self.io(self.storage.delete, identity, key, deadline)
        return {'schemaVersion': '1.0', 'status': fenced.get('cleanupStatus', 'cleanup_pending'), 'operationId': operation_id}
