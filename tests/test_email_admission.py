"""Offline durable-journal and HTTP admission contracts; no provider/network IO."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
from threading import Barrier, Event

from fastapi.testclient import TestClient
import httpx
import pytest

from app.adapters.auth import AuthFailure
from app.config import Settings
from app.main import create_app
from app.services.email_admission import EmailAdmission, MAX_FILE_BYTES
from test_auth import EMAIL, FakeAuth, ORIGIN, PAYLOAD, SETTINGS, headers, post


@pytest.fixture
def journal(tmp_path):
    path = tmp_path / 'synthetic.sqlite3'
    now = [1000.0]
    EmailAdmission.initialize(path, clock=lambda: now[0])
    return path, now, EmailAdmission(path, clock=lambda: now[0])


def rows(path):
    with sqlite3.connect(path) as connection:
        return connection.execute('SELECT recipient, reserved_at FROM reservations').fetchall()


def test_normalization_rolling_boundary_global_limit_and_bounded_storage(journal):
    path, now, service = journal
    service.reserve('  TÉSTER@EXAMPLE.TEST  ')
    with pytest.raises(AuthFailure, match='auth_capacity'):
        service.reserve('téster@example.test')
    now[0] = 1000.5
    service.reserve('other@example.test')
    with pytest.raises(AuthFailure, match='auth_capacity'):
        service.reserve('third@example.test')
    now[0] = 4599.999
    with pytest.raises(AuthFailure, match='auth_capacity'):
        service.reserve('TÉSTER@EXAMPLE.TEST')
    now[0] = 4600.0
    service.reserve('téster@example.test')
    assert sorted(timestamp for _, timestamp in rows(path)) == [1000.5, 4600.0]
    for index in range(100):
        now[0] += 3600
        service.reserve(f'{index}@example.test')
    assert len(rows(path)) <= 2
    assert path.stat().st_size <= MAX_FILE_BYTES
    content = path.read_bytes()
    assert b'example.test' not in content and b'TEST_PASSWORD' not in content


def test_exclusive_initialization_and_process_reopen_keep_reservation(journal, monkeypatch, capsys):
    path, _, service = journal
    service.reserve(EMAIL)
    before = path.read_bytes()
    with pytest.raises(AuthFailure):
        EmailAdmission.initialize(path)
    assert path.read_bytes() == before
    code = ('from app.services.email_admission import EmailAdmission; '
            'from app.adapters.auth import AuthFailure; '
            's=EmailAdmission(__import__("sys").argv[1], clock=lambda: 1000); '
            '\ntry: s.reserve("tester@example.test")'
            '\nexcept AuthFailure as error: raise SystemExit(0 if error.code == "auth_capacity" else 2)'
            '\nraise SystemExit(3)')
    result = subprocess.run([sys.executable, '-c', code, str(path)], capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr.decode()
    from scripts.email_admission import main
    fresh = path.parent / 'cli.sqlite3'
    monkeypatch.setattr(sys, 'argv', ['email_admission', 'init', str(fresh)])
    main()
    assert 'initialized' in capsys.readouterr().out
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert EMAIL not in capsys.readouterr().err


@pytest.mark.parametrize('kind', ['missing', 'corrupt', 'schema', 'version', 'secret', 'clock',
                                  'future_row', 'oversized', 'sidecar'])
def test_unsafe_journal_fails_closed_without_reset(journal, kind):
    path, now, service = journal
    service.reserve(EMAIL)
    if kind == 'missing':
        path.unlink()
    elif kind == 'corrupt':
        path.write_bytes(b'invalid sqlite synthetic state')
    elif kind == 'oversized':
        with path.open('ab') as target:
            target.write(b'x' * MAX_FILE_BYTES)
    elif kind == 'sidecar':
        Path(str(path) + '-wal').write_bytes(b'unsafe')
    elif kind == 'clock':
        now[0] -= .001
    else:
        with sqlite3.connect(path) as connection:
            connection.execute({
                'schema': 'CREATE TABLE unexpected (value TEXT)',
                'version': 'UPDATE metadata SET version = 2',
                'secret': "UPDATE metadata SET secret = X'00'",
                'future_row': 'UPDATE reservations SET reserved_at = 1001',
            }[kind])
    before = path.read_bytes() if path.exists() else None
    with pytest.raises(AuthFailure) as error:
        service.reserve('other@example.test')
    assert error.value.code == 'auth_unavailable'
    assert (path.read_bytes() if path.exists() else None) == before


def test_locked_and_unwritable_journal_fail_closed(journal):
    path, _, service = journal
    with sqlite3.connect(path, timeout=0) as blocker:
        blocker.execute('BEGIN EXCLUSIVE')
        with pytest.raises(AuthFailure):
            service.reserve(EMAIL)
    assert not rows(path)
    path.chmod(stat.S_IREAD)
    try:
        with pytest.raises(AuthFailure):
            service.reserve(EMAIL)
    finally:
        path.chmod(stat.S_IREAD | stat.S_IWRITE)
    assert not rows(path)


@pytest.mark.parametrize('same_recipient', [False, True])
def test_concurrent_separate_instances_never_exceed_combined_limits(journal, same_recipient):
    path, now, _ = journal
    barrier = Barrier(8)

    def reserve(index):
        service = EmailAdmission(path, clock=lambda: now[0])
        barrier.wait(timeout=5)
        try:
            service.reserve(EMAIL if same_recipient else f'{index}@example.test')
            return True
        except AuthFailure:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        admitted = list(pool.map(reserve, range(8)))
    assert 1 <= sum(admitted) <= (1 if same_recipient else 2)
    assert len(rows(path)) == sum(admitted)


def test_async_journal_jobs_have_bounded_admission(journal):
    _, _, service = journal
    entered, release = Barrier(3), Event()

    def blocked(recipient):
        entered.wait(timeout=5)
        assert release.wait(timeout=5)

    service.reserve = blocked

    async def exercise():
        first = asyncio.create_task(service.reserve_for_dispatch(EMAIL))
        second = asyncio.create_task(service.reserve_for_dispatch(EMAIL))
        await asyncio.to_thread(entered.wait, 5)
        try:
            with pytest.raises(AuthFailure, match='auth_capacity'):
                await service.reserve_for_dispatch(EMAIL)
        finally:
            release.set()
        await asyncio.gather(first, second)

    asyncio.run(exercise())


def test_cancellation_before_worker_start_keeps_owned_capacity_until_completion(journal, monkeypatch):
    import app.services.email_admission as admission
    _, _, service = journal

    async def exercise():
        scheduled, release = asyncio.Event(), asyncio.Event()
        count = 0

        async def delayed_pool(operation, recipient):
            nonlocal count
            count += 1
            if count == 2:
                scheduled.set()
            await release.wait()

        monkeypatch.setattr(admission, 'run_in_threadpool', delayed_pool)
        waiters = [asyncio.create_task(service.reserve_for_dispatch(EMAIL)) for _ in range(2)]
        await scheduled.wait()
        for waiter in waiters:
            waiter.cancel()
        await asyncio.gather(*waiters, return_exceptions=True)
        with pytest.raises(AuthFailure):
            await service.reserve_for_dispatch(EMAIL)
        owned = list(admission._jobs)
        release.set()
        await asyncio.gather(*owned)
        await service.reserve_for_dispatch(EMAIL)

    asyncio.run(exercise())


def client_for(service=None, *, registry=None, settings=SETTINGS):
    adapter = FakeAuth()
    app = create_app(settings, auth_adapter=adapter, email_admission=service, registry=registry)
    return TestClient(app, base_url=ORIGIN), adapter, app


def test_fresh_browsers_share_recipient_and_global_capacity_across_purposes(journal):
    path, now, service = journal
    client, adapter, app = client_for(service)
    assert post(client).status_code == 200
    fresh = TestClient(app, base_url=ORIGIN)
    response = post(fresh, 'recovery/request', {'email': '  TESTER@EXAMPLE.TEST  '})
    assert response.status_code == 429
    assert len(app.state.auth_registry.pending) == 1
    assert adapter.calls == ['signup']
    assert post(fresh, 'recovery/request', {'email': 'second@example.test'}).status_code == 200
    third = TestClient(app, base_url=ORIGIN)
    assert post(third, payload={**PAYLOAD, 'email': 'third@example.test'}).status_code == 429
    assert adapter.calls == ['signup', 'request_recovery']
    assert len(rows(path)) == 2
    # A new application/registry/service still sees both durable reservations.
    restarted, offline, _ = client_for(EmailAdmission(path, clock=lambda: now[0]))
    assert post(restarted).status_code == 429
    assert not offline.calls


@pytest.mark.parametrize('action,payload', [('signup', PAYLOAD), ('recovery/request', {'email': EMAIL})])
def test_provider_failure_retains_reservation_and_discards_pending(journal, action, payload):
    path, now, service = journal
    client, adapter, app = client_for(service)
    adapter.fail = True
    assert post(client, action, payload).status_code == 503
    assert not app.state.auth_registry.pending
    assert len(rows(path)) == 1
    restarted, offline, _ = client_for(EmailAdmission(path, clock=lambda: now[0]))
    assert post(restarted, action, payload).status_code == 429
    assert not offline.calls


@pytest.mark.parametrize('failure', ['write', 'before_commit', 'after_commit'])
@pytest.mark.parametrize('action,payload', [('signup', PAYLOAD), ('recovery/request', {'email': EMAIL})])
def test_persistence_failure_prevents_http_dispatch_and_preserves_transaction_boundary(
        journal, monkeypatch, failure, action, payload):
    path, now, service = journal
    service.reserve('previous@example.test')
    previous = rows(path)
    now[0] += 3600
    connect = service._connect

    class FailingConnection:
        def __init__(self):
            self.real = connect()

        def execute(self, statement, *args):
            if failure == 'write' and statement.startswith('INSERT INTO reservations'):
                raise sqlite3.OperationalError('synthetic write failure')
            return self.real.execute(statement, *args)

        def commit(self):
            if failure == 'after_commit':
                self.real.commit()
            raise sqlite3.OperationalError('synthetic uncertain commit failure')

        def close(self):
            self.real.close()

    monkeypatch.setattr(service, '_connect', FailingConnection)
    client, adapter, app = client_for(service)
    response = post(client, action, payload)
    assert response.status_code == 503
    assert response.json()['code'] == 'auth_unavailable'
    assert not adapter.calls and not app.state.auth_registry.pending
    assert 'synthetic' not in response.text and str(path) not in response.text
    with sqlite3.connect(path) as connection:
        last_seen = connection.execute('SELECT last_seen FROM metadata').fetchone()[0]
    if failure == 'after_commit':
        assert len(rows(path)) == 1 and rows(path) != previous
        assert last_seen == now[0]
    else:
        # Closing an uncommitted connection must undo pruning and the clock update too.
        assert rows(path) == previous
        assert last_seen == 1000.0
    restarted, offline, _ = client_for(EmailAdmission(path, clock=lambda: now[0]))
    retry = post(restarted, action, payload)
    assert retry.status_code == (429 if failure == 'after_commit' else 200)
    assert offline.calls == ([] if failure == 'after_commit' else
                             ['signup' if action == 'signup' else 'request_recovery'])


@pytest.mark.parametrize('action,payload', [('signup', PAYLOAD), ('recovery/request', {'email': EMAIL})])
def test_cancelled_http_waiters_keep_real_commits_without_dispatch_and_release_slots(
        journal, monkeypatch, action, payload):
    import app.services.email_admission as admission
    path, now, first_service = journal
    other_path = path.parent / 'second-cancelled.sqlite3'
    EmailAdmission.initialize(other_path, clock=lambda: now[0])
    services = [first_service, EmailAdmission(other_path, clock=lambda: now[0])]
    entered, release = Barrier(3), Event()

    def held_connection(connect):
        class HeldConnection:
            def __init__(self):
                self.real = connect()

            def execute(self, statement, *args):
                return self.real.execute(statement, *args)

            def commit(self):
                entered.wait(timeout=5)
                assert release.wait(timeout=5)
                self.real.commit()

            def close(self):
                self.real.close()

        return HeldConnection

    apps, adapters = [], []
    for service in services:
        monkeypatch.setattr(service, '_connect', held_connection(service._connect))
        _, adapter, app = client_for(service)
        apps.append(app)
        adapters.append(adapter)

    async def exercise():
        async with (httpx.AsyncClient(transport=httpx.ASGITransport(apps[0]), base_url=ORIGIN) as one,
                    httpx.AsyncClient(transport=httpx.ASGITransport(apps[1]), base_url=ORIGIN) as two):
            clients = [one, two]
            protected = []
            for client in clients:
                status = await client.get('/api/v1/auth/status')
                protected.append({'Origin': ORIGIN, 'X-CSRF-Token': status.json()['csrfToken']})

            def requests():
                return [asyncio.create_task(client.post('/api/v1/auth/' + action, json=payload, headers=csrf))
                        for client, csrf in zip(clients, protected)]

            waiters = requests()
            try:
                await asyncio.to_thread(entered.wait, 5)
                owned = list(admission._jobs)
                assert len(owned) == 2
                for waiter in waiters:
                    waiter.cancel()
                results = await asyncio.gather(*waiters, return_exceptions=True)
                assert all(isinstance(result, asyncio.CancelledError) for result in results)
                assert all(not job.done() for job in owned)
                assert not rows(path) and not rows(other_path)
                denied = await one.post('/api/v1/auth/' + action, json=payload, headers=protected[0])
                assert denied.status_code == 429
                assert all(not adapter.calls for adapter in adapters)
            finally:
                release.set()
                await asyncio.gather(*list(admission._jobs))
            assert all(not adapter.calls for adapter in adapters)
            for journal_path in (path, other_path):
                assert len(rows(journal_path)) == 1
                with pytest.raises(AuthFailure, match='auth_capacity'):
                    EmailAdmission(journal_path, clock=lambda: now[0]).reserve(EMAIL)
            # Both real workers must be admitted again, concurrently, after expiry.
            now[0] += 3600
            retries = requests()
            await asyncio.to_thread(entered.wait, 5)
            assert [response.status_code for response in await asyncio.gather(*retries)] == [200, 200]
            expected = 'signup' if action == 'signup' else 'request_recovery'
            assert all(adapter.calls == [expected] for adapter in adapters)

    asyncio.run(exercise())


@pytest.mark.parametrize('kind', ['csrf', 'body', 'oversized', 'pending'])
@pytest.mark.parametrize('action', ['signup', 'recovery/request'])
def test_rejected_requests_never_reserve_or_dispatch(journal, kind, action):
    path, _, service = journal
    client, adapter, app = client_for(service)
    protected_headers = headers(client)
    before = path.read_bytes()
    payload = PAYLOAD if action == 'signup' else {'email': EMAIL}
    if kind == 'csrf':
        protected_headers['X-CSRF-Token'] = 'invalid'
    elif kind == 'body':
        payload = {'email': 'invalid'}
    elif kind == 'oversized':
        payload = {'email': 'x' * 8193}
    else:
        browser_id = client.cookies['sb_browser']
        for _ in range(4):
            app.state.auth_registry.start_attempt(browser_id, EMAIL)
    response = client.post('/api/v1/auth/' + action, json=payload, headers=protected_headers)
    assert response.status_code == {'csrf': 403, 'body': 422, 'oversized': 422, 'pending': 429}[kind]
    assert not adapter.calls
    assert path.read_bytes() == before


@pytest.mark.parametrize('configured', [False, True])
def test_default_gate_without_safe_state_preserves_password_login_and_demo(tmp_path, configured):
    settings = replace(SETTINGS, auth_email_admission_path=str(tmp_path / 'missing.sqlite3')) if configured else SETTINGS
    client, adapter, app = client_for(settings=settings)
    assert settings.available
    assert post(client).status_code == 503
    assert post(client, 'recovery/request', {'email': EMAIL}).status_code == 503
    assert not app.state.auth_registry.pending and not adapter.calls
    assert post(client, 'login').status_code == 200
    assert adapter.calls == ['login']
    assert client.get('/api/v1/demo/fixture').status_code == 200
    assert not (tmp_path / 'missing.sqlite3').exists()


def test_server_only_configuration_and_dedicated_secret(journal, monkeypatch, tmp_path):
    path, _, _ = journal
    other = tmp_path / 'other.sqlite3'
    EmailAdmission.initialize(other)
    with sqlite3.connect(path) as one, sqlite3.connect(other) as two:
        assert one.execute('SELECT secret FROM metadata').fetchone() != two.execute('SELECT secret FROM metadata').fetchone()
    monkeypatch.setenv('AUTH_EMAIL_ADMISSION_PATH', str(path))
    assert Settings.from_env().auth_email_admission_path == str(path)
