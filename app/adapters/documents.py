"""User-JWT RPC client. Gate headers are sourced only from server configuration."""
from contextlib import contextmanager
import json
import time
import httpx
from app.adapters.auth import BudgetTransport, BudgetNetworkBackend, OperationBudget


class DocumentFailure(Exception):
    def __init__(self, code='save_pending'):
        self.code = code
        super().__init__(code)


class SupabaseDocuments:
    def __init__(self, settings, *, transport=None):
        self.settings, self.transport = settings, transport

    @contextmanager
    def client(self, identity, deadline, *, verification=False):
        budget = OperationBudget(max(0, deadline - time.monotonic()), time.monotonic)
        transport = self.transport
        if transport is None:
            transport = httpx.HTTPTransport(retries=0, trust_env=False)
            transport._pool._network_backend = BudgetNetworkBackend(budget)
        headers = {'apikey': self.settings.supabase_key, 'Authorization': 'Bearer ' + identity.access_token,
                   'x-studybuddy-backend': self.settings.save_backend_key()}
        if verification:
            headers['x-studybuddy-operation'] = 'verify'
        with httpx.Client(headers=headers, timeout=httpx.Timeout(5, connect=3), follow_redirects=False,
                          trust_env=False, transport=BudgetTransport(transport, budget)) as client:
            yield client

    def call(self, identity, action, payload, deadline):
        if action not in {'get', 'pending', 'library', 'file', 'reload', 'admit', 'attempt', 'verified', 'commit', 'cancel', 'progress_read', 'progress_write'}:
            raise DocumentFailure('save_unavailable')
        try:
            with self.client(identity, deadline) as client:
                with client.stream('POST', self.settings.supabase_url + '/rest/v1/rpc/sb_save_' + action + '_v1',
                                   json={'payload': payload}) as response:
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        if len(raw) + len(chunk) > 2 * 1024 * 1024:
                            raise DocumentFailure()
                        raw.extend(chunk)
                    value = json.loads(raw)
                    if response.status_code != 200:
                        raise DocumentFailure('save_unavailable' if response.status_code in (401, 403) else 'save_pending')
                    if not isinstance(value, dict):
                        raise DocumentFailure()
                    if value.get('error'):
                        raise DocumentFailure(value['error'] if value['error'] in {
                            'save_conflict', 'save_mismatch', 'save_expired', 'save_unknown', 'file_required',
                            'document_unknown', 'file_unavailable', 'progress_pending', 'progress_conflict',
                            'progress_mismatch', 'progress_generation'} else 'save_pending')
                    return value
        except DocumentFailure:
            raise
        except Exception:
            raise DocumentFailure() from None
