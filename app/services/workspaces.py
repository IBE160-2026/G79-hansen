"""Metadata-only, session-owned ordered commands and atomic publication/Save fence.

Lock order is always authentication registry then workspace registry. No external
await occurs with either lock held. Ended sessions remove all records immediately.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from threading import RLock
from uuid import uuid4
import asyncio
from contextlib import asynccontextmanager

from app.services.receipts import Proofs, acceptance_projection, digest


class WorkspaceFailure(Exception):
    def __init__(self, code='stale_workspace'):
        self.code = code
        super().__init__(code)


@dataclass(repr=False)
class Workspace:
    sequence: int = 0
    revision: int = -1
    command_hash: str = ''
    operation: str = ''
    acceptance_hash: str | None = None
    file_hash: str | None = None
    receipt_id: str | None = None
    bundle_hash: str | None = None
    admission_gate: object = None


class Workspaces:
    def __init__(self, registry, *, proofs=None):
        self.registry = registry
        self.proofs = proofs or Proofs()
        self.records = {}
        self.lock = RLock()
        registry.end_listeners.append(self.remove_session)

    def remove_session(self, session_id):
        with self.lock:
            self.records.pop(session_id, None)

    @contextmanager
    def locked(self, session_id, session, workspace_id, *, create=False):
        with self.registry.lock:
            self.registry.live_session(session_id, session)
            with self.lock:
                table = self.records.get(session_id)
                if table is None:
                    if not create:
                        raise WorkspaceFailure()
                    table = self.records[session_id] = {}
                if workspace_id not in table:
                    if not create:
                        raise WorkspaceFailure()
                    if len(table) >= 8:
                        raise WorkspaceFailure('workspace_capacity')
                    table[workspace_id] = Workspace()
                yield table[workspace_id]

    def gate(self, session_id, session, workspace_id):
        with self.locked(session_id, session, workspace_id, create=True) as record:
            if record.admission_gate is None:
                record.admission_gate = asyncio.Lock()
            return record.admission_gate

    async def ordered_command(self, session_id, session, workspace_id, *args):
        async with self.gate(session_id, session, workspace_id):
            return self.command(session_id, session, workspace_id, *args)

    @asynccontextmanager
    async def admit_save(self, session_id, session, token, acceptance, bundle):
        """Own one workspace gate, with no registry/auth lock around remote IO.

        Logout detaches the record immediately. The live check immediately before
        yield authorizes only this already-dispatched explicit admission.
        """
        async with self.gate(session_id, session, acceptance.workspace_id):
            with self.validate_save(session_id, session, token, acceptance, bundle) as claims:
                pass
            self.registry.live_session(session_id, session)
            yield claims

    def command(self, session_id, session, workspace_id, revision, sequence, operation, payload):
        if hasattr(payload, 'model_dump'):
            payload = payload.model_dump(mode='json', by_alias=True)
        command_hash = digest({'operation': operation, 'payload': payload})
        with self.locked(session_id, session, workspace_id, create=True) as record:
            if sequence == record.sequence and command_hash == record.command_hash:
                if operation == 'invalidate':
                    return False
                raise WorkspaceFailure('command_replayed')
            if sequence <= record.sequence or revision < record.revision:
                raise WorkspaceFailure()
            if operation == 'generate' and revision != record.revision:
                raise WorkspaceFailure()
            record.sequence, record.revision = sequence, revision
            record.command_hash, record.operation = command_hash, operation
            record.receipt_id = record.bundle_hash = None
            if operation != 'generate':
                record.acceptance_hash = record.file_hash = None
            return True

    def claims(self, session_id, session, workspace_id, revision):
        now = self.registry.clock()
        return {'ownerId': session.identity.owner_id, 'sessionBinding': digest({'session': session_id}),
                'workspaceId': workspace_id, 'revision': revision, 'issuedAt': now,
                'expiresAt': min(now + 1800, session.touched + self.registry.idle_seconds,
                                 session.created + self.registry.absolute_seconds)}

    def accept(self, session_id, session, submitted, result, file_hash):
        result.workspace_id = submitted.workspaceId
        result.command_sequence = submitted.commandSequence
        accepted_hash = digest(acceptance_projection(result))
        with self.locked(session_id, session, submitted.workspaceId) as record:
            self.current(record, submitted.clientRevision, submitted.commandSequence, 'extract')
            record.acceptance_hash, record.file_hash = accepted_hash, file_hash
            result.source_proof = self.proofs.sign('source', {
                **self.claims(session_id, session, submitted.workspaceId, submitted.clientRevision),
                'acceptanceHash': accepted_hash, 'fileHash': file_hash})
        return result

    @staticmethod
    def current(record, revision, sequence, operation):
        if (record.revision, record.sequence, record.operation) != (revision, sequence, operation):
            raise WorkspaceFailure()

    def check_claims(self, claims, session_id, session, workspace_id, revision):
        if (claims.get('ownerId') != session.identity.owner_id or claims.get('sessionBinding') != digest({'session': session_id}) or
            claims.get('workspaceId') != workspace_id or claims.get('revision') != revision or
            claims.get('expiresAt', 0) <= self.registry.clock()):
            raise WorkspaceFailure('invalid_proof')

    def verify_source(self, session_id, session, submitted):
        accepted = submitted.acceptance
        claims = self.proofs.verify('source', accepted.source_proof)
        self.check_claims(claims, session_id, session, submitted.workspace_id, submitted.client_revision)
        with self.locked(session_id, session, submitted.workspace_id) as record:
            if (accepted.workspace_id != submitted.workspace_id or accepted.client_revision != submitted.client_revision or
                claims.get('acceptanceHash') != digest(acceptance_projection(accepted)) or
                claims.get('acceptanceHash') != record.acceptance_hash or claims.get('fileHash') != record.file_hash):
                raise WorkspaceFailure('invalid_proof')
        return claims

    def publish(self, session_id, session, submitted, bundle):
        with self.locked(session_id, session, submitted.workspace_id) as record:
            self.current(record, submitted.client_revision, submitted.command_sequence, 'generate')
            record.receipt_id, record.bundle_hash = str(uuid4()), digest(bundle)
            claims = {**self.claims(session_id, session, submitted.workspace_id, submitted.client_revision),
                      'commandSequence': submitted.command_sequence, 'generationId': bundle.generation_id,
                      'receiptId': record.receipt_id, 'sourceHash': digest(bundle.source),
                      'settingsHash': digest(bundle.settings), 'bundleHash': record.bundle_hash,
                      'acceptanceHash': record.acceptance_hash, 'fileHash': record.file_hash}
            return self.proofs.sign('generation', claims)

    def validate_save(self, session_id, session, token, acceptance, bundle):
        """Synchronous authority check. Durable callers use admit_save's owned gate."""
        return self._save_admission(session_id, session, token, acceptance, bundle)

    @contextmanager
    def _save_admission(self, session_id, session, token, acceptance, bundle):
        claims = self.proofs.verify('generation', token)
        workspace_id = claims.get('workspaceId')
        with self.locked(session_id, session, workspace_id) as record:
            self.check_claims(claims, session_id, session, workspace_id, acceptance.client_revision)
            self.current(record, acceptance.client_revision, claims.get('commandSequence'), 'generate')
            if (claims.get('receiptId') != record.receipt_id or claims.get('bundleHash') != record.bundle_hash or
                claims.get('bundleHash') != digest(bundle) or claims.get('sourceHash') != digest(bundle.source) or
                claims.get('settingsHash') != digest(bundle.settings) or
                claims.get('acceptanceHash') != digest(acceptance_projection(acceptance)) or
                claims.get('acceptanceHash') != record.acceptance_hash or claims.get('fileHash') != record.file_hash or
                claims.get('generationId') != bundle.generation_id):
                raise WorkspaceFailure('invalid_proof')
        yield claims
