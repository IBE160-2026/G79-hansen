"""Offline evaluation controls; no real keys, ledgers, grants or provider calls."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path
import subprocess
import sys
import threading

import httpx
import pytest
from pypdf import PdfReader

from app.adapters.model import MODEL
from app.config import Settings
from app.services.model_budget import BudgetFailure, ModelBudget
from app.services.receipts import canonical
from scripts import content_evaluation as evaluation


@pytest.fixture(scope='module')
def registered():
    return evaluation.registration()


@pytest.fixture
def setup(tmp_path, registered):
    data, accepted = registered
    evidence = tmp_path / 'evidence'
    evaluation.register(data, evidence)
    grant_path, ledger_path = tmp_path / 'grant.json', tmp_path / 'global.json'
    evaluation.EvaluationGrant.initialize(grant_path)
    ModelBudget.initialize(ledger_path)
    settings = Settings(model_enabled=True, openai_api_key='SYNTHETIC_KEY', model_budget_path=str(ledger_path))
    return {'settings': settings, 'data': data, 'accepted': accepted,
            'grant_path': grant_path, 'evidence_dir': evidence}


def empty_output():
    return {**{part: [] for part in evaluation.PARTS}, 'warnings': [],
        'insufficiency': {part: 'The source contains punctuation only, with no factual evidence for this section.'
                         for part in evaluation.PARTS}}


def provider(output=None, **changes):
    return {'status': 'completed', 'model': MODEL,
        'usage': {'input_tokens': 100, 'output_tokens': 50},
        'output': [{'type': 'message', 'status': 'completed', 'content': [
            {'type': 'output_text', 'text': json.dumps(output or empty_output())}]}],
        'privateEnvelope': 'NEVER_PERSIST_ENVELOPE', **changes}


def transport(calls, response=None, *, status=200):
    def handler(request):
        calls.append(json.loads(request.content))
        assert request.headers['authorization'] == 'Bearer SYNTHETIC_KEY'
        return httpx.Response(status, stream=httpx.ByteStream(canonical(response or provider())))
    return httpx.MockTransport(handler)


def run(setup, calls=None, **kwargs):
    return asyncio.run(evaluation.run_case('E', **setup,
        transport=transport(calls if calls is not None else []), **kwargs))


def test_registered_exact_inputs_settings_concepts_and_locations(registered):
    data, accepted = registered
    corpus = evaluation.fixtures()
    assert len(corpus.CONCEPTS) == 3
    assert sum(len(value) for value in corpus.CONCEPTS.values()) == 15
    for case in ('A', 'B'):
        source = accepted[case]
        assert [unit.text for unit in source.source.units] == list(getattr(corpus, 'SOURCE_' + case))
        assert [unit.location for unit in source.source.units] == [1, 2, 3, 4, 5]
    assert accepted['A'].kind == 'paste'
    assert accepted['B'].kind == 'text-file'
    assert accepted['B'].settings.language == 'en' and accepted['B'].settings.detail == 'detailed'
    assert accepted['C'].settings.language == 'nb' and accepted['C'].settings.detail == 'detailed'
    assert accepted['D'].settings.subject == corpus.CONFLICT
    assert accepted['E'].source.units[0].text == '...'
    assert [concept['id'] for concept in data['cases']['D']['concepts']] == ['A1', 'A2', 'A3', 'A4', 'A5']
    assert data['semanticAssessment'] == 'pending'


def test_pdf_has_ordinary_visible_font_exact_lines_and_physical_gaps(registered):
    data, accepted = registered
    corpus = evaluation.fixtures()
    raw = corpus.readable_pdf()
    assert raw == corpus.readable_pdf()
    assert b'/ToUnicode' not in raw and b'/WinAnsiEncoding' in raw and b'/Helvetica' in raw
    reader = PdfReader(io.BytesIO(raw))
    assert len(reader.pages) == 5
    assert [page.extract_text().splitlines() for page in reader.pages] == [
        [line for line in lines if line] for lines in corpus.pdf_lines()]
    assert [unit.location for unit in accepted['C'].source.units] == [1, 3, 5]
    assert accepted['C'].unreadable_pages == [2, 4]
    assert [concept['location'] for concept in data['cases']['C']['concepts']] == [1, 1, 3, 3, 5]


def test_offline_default_and_case_without_opt_in_never_read_configuration_or_grant(monkeypatch, registered, capsys):
    monkeypatch.setattr(evaluation, 'registration', lambda: registered)
    monkeypatch.setattr(evaluation.Settings, 'from_env', lambda: pytest.fail('offline config read'))
    monkeypatch.setattr(evaluation.EvaluationGrant, '__init__', lambda *_: pytest.fail('offline grant access'))
    for args in ([], ['--case', 'A']):
        assert evaluation.main(args) == 0
    assert all(json.loads(line)['offline'] for line in capsys.readouterr().out.splitlines())


def test_live_requires_exactly_one_selected_case(monkeypatch, registered, capsys):
    monkeypatch.setattr(evaluation, 'registration', lambda: registered)
    monkeypatch.setattr(evaluation.Settings, 'from_env', lambda: pytest.fail('missing case read config'))
    assert evaluation.main(['--live']) == 1
    assert json.loads(capsys.readouterr().out)['statusCode'] == 8


@pytest.mark.parametrize('bad', ['missing', 'malformed', 'duplicate', 'oversized', 'boolean', 'extra', 'exhausted', 'changed_cap', 'negative'])
def test_missing_corrupt_or_exhausted_grant_blocks_before_global_or_transport(setup, bad):
    path = setup['grant_path']
    if bad == 'missing':
        path.unlink()
    else:
        value = evaluation.EvaluationGrant.initial()
        if bad == 'malformed': raw = '{'
        elif bad == 'duplicate': raw = '{"version":1,"version":1,"maximumAttempts":8,"reservationMicrousd":50000,"attempts":0}'
        elif bad == 'oversized': raw = ' ' * 513
        else:
            if bad == 'boolean': value['attempts'] = False
            elif bad == 'extra': value['private'] = 'not allowed'
            elif bad == 'exhausted': value['attempts'] = 8
            elif bad == 'changed_cap': value['maximumAttempts'] = 9
            elif bad == 'negative': value['attempts'] = -1
            raw = json.dumps(value)
        path.write_text(raw, encoding='ascii')
    calls = []
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        run(setup, calls)
    assert failure.value.code == 2 and calls == []
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 0


def test_exclusive_initialization_never_resets_grant(setup):
    grant = evaluation.EvaluationGrant(setup['grant_path'])
    with grant.claim(): pass
    with pytest.raises(FileExistsError):
        evaluation.EvaluationGrant.initialize(setup['grant_path'])
    assert grant.read()['attempts'] == 1


def test_global_reservation_happens_only_after_durable_grant_consumption(setup, monkeypatch):
    observed = []
    reserve = ModelBudget.reserve
    def checked_reserve(self, **kwargs):
        assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
        observed.append('global')
        return reserve(self, **kwargs)
    monkeypatch.setattr(ModelBudget, 'reserve', checked_reserve)
    calls = []
    result = run(setup, calls)
    assert observed == ['global'] and len(calls) == 1
    assert result['status'] == 'structurally_validated' and result['semanticAssessment'] == 'pending'
    ledger = ModelBudget(setup['settings'].model_budget_path).read()
    assert ledger['attempts'] == 1 and ledger['liveChecks'] == 0
    assert ledger['reservedMicrousd'] == 50_000


@pytest.mark.parametrize('global_failure', ['missing', 'blocked', 'exhausted', 'corrupt'])
def test_global_failure_loses_grant_without_dispatch_or_refund(setup, global_failure):
    ledger = ModelBudget(setup['settings'].model_budget_path)
    if global_failure == 'missing': ledger.path.unlink()
    elif global_failure == 'blocked': ledger.block()
    elif global_failure == 'corrupt': ledger.path.write_text('{}')
    else:
        value = ledger.initial(); value.update(attempts=100, reservedMicrousd=5_000_000)
        ledger.write(value)
    calls = []
    result = run(setup, calls)
    assert result['errorCode'] == 3 and calls == []
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
    assert json.loads((setup['evidence_dir'] / 'attempt-01-E-initial.json').read_text()) == result


def test_concurrent_instances_and_threads_fail_without_dispatch(setup):
    first = evaluation.EvaluationGrant(setup['grant_path'])
    with first.claim():
        with pytest.raises(BudgetFailure):
            with first.claim(): pass
        with ThreadPoolExecutor(1) as pool:
            future = pool.submit(run, setup)
            with pytest.raises(evaluation.EvaluationFailure) as failure:
                future.result(timeout=2)
            assert failure.value.code == 2
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 0
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1


def test_eight_restarted_attempts_preserve_evidence_and_reject_ninth(setup):
    calls = []
    for attempt in range(1, 9):
        result = run(setup, calls, phase='initial' if attempt == 1 else 'recheck')
        assert result['grantAttempt'] == attempt
    with pytest.raises(evaluation.EvaluationFailure):
        run(setup, calls)
    assert len(calls) == 8
    assert len(list(setup['evidence_dir'].glob('attempt-*.json'))) == 8
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 8
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 8


@pytest.mark.parametrize('failure', ['http', 'invalid', 'usage', 'unknown_reference', 'timeout'])
def test_failed_or_uncertain_dispatch_consumes_both_and_stores_only_safe_evidence(setup, monkeypatch, failure):
    value = provider()
    if failure == 'invalid': value['output'][0]['content'][0]['text'] = 'PRIVATE_PROVIDER_ERROR'
    elif failure == 'usage': value['usage']['output_tokens'] = 8001
    elif failure == 'unknown_reference':
        output = empty_output()
        output['summary'] = [{'text': 'Synthetic assertion', 'references': ['u99']}]
        value = provider(output)
    calls = []
    mock = transport(calls, value, status=503 if failure == 'http' else 200)
    if failure == 'timeout':
        monkeypatch.setattr(evaluation, 'DEADLINE_SECONDS', .1)
        async def held(_request):
            calls.append(True)
            await asyncio.sleep(1)
        mock = httpx.MockTransport(held)
    result = asyncio.run(evaluation.run_case('E', **setup, transport=mock))
    assert result['status'] == 'failed' and result['errorCode'] != 0 and len(calls) == 1
    assert result['globalReservationCompleted'] is True and result['providerAttemptStarted'] is True
    if failure in ('http', 'invalid', 'unknown_reference'):
        assert result['inputTokens'] == 100 and result['outputTokens'] == 50
        assert result['estimatedUsd'] == .000035
    ledger = ModelBudget(setup['settings'].model_budget_path).read()
    assert ledger['attempts'] == 1 and ledger['reservedMicrousd'] == 50_000
    assert ledger['blocked'] is (failure == 'usage')
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
    raw = (setup['evidence_dir'] / 'attempt-01-E-initial.json').read_text()
    assert all(secret not in raw for secret in ('PRIVATE_PROVIDER_ERROR', 'NEVER_PERSIST_ENVELOPE', 'SYNTHETIC_KEY', 'Authorization', 'receipt', 'sourceProof'))


def test_projection_contains_all_item_text_and_canonical_references_only(setup):
    output = empty_output()
    output['warnings'] = ['Synthetic warning retained exactly.']
    output.update(summary=[{'text': 'Ordinary books have a 14-day loan period.', 'references': ['u1']}],
        concepts=[{'term': 'Loan period', 'explanation': 'Fourteen days for ordinary books.', 'references': ['u1']}],
        flashcards=[{'question': 'How long?', 'answer': '14 days.', 'references': ['u1']}],
        quiz=[{'question': 'Name the period.', 'answer': '14 days.', 'references': ['u1']}])
    calls = []
    result = asyncio.run(evaluation.run_case('A', **setup, transport=transport(calls, provider(output))))
    assert result['status'] == 'structurally_validated'
    assert set(result['output']) == {*evaluation.PARTS, 'warnings', 'insufficiency'}
    for part in evaluation.PARTS:
        assert result['output'][part][0]['references'] == [{'sourceUnitId': 'paragraph-1', 'label': 'Avsnitt 1'}]
        for field, value in output[part][0].items():
            if field != 'references':
                assert result['output'][part][0][field] == value
    assert result['output']['warnings'] == output['warnings']
    assert result['output']['insufficiency'] == output['insufficiency']
    saved = json.loads((setup['evidence_dir'] / 'attempt-01-A-initial.json').read_text(encoding='utf-8'))
    assert saved['output'] == result['output']
    raw = json.dumps(result)
    assert all(secret not in raw for secret in ('generationId', 'sourceProof', 'receipt', 'SYNTHETIC_KEY', 'NEVER_PERSIST_ENVELOPE'))


def test_registration_mismatch_or_missing_blocks_before_either_allowance(setup):
    directory = evaluation.registration_directory(setup['data'], setup['evidence_dir'])
    (directory / 'source-c.pdf').write_bytes(b'changed')
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        run(setup)
    assert failure.value.code == 7
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 0
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 0


def test_existing_evidence_blocks_before_allowances_or_dispatch(setup):
    (setup['evidence_dir'] / 'attempt-01-E-initial.json').write_text('prior evidence')
    calls = []
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        run(setup, calls)
    assert failure.value.code == 6
    assert (setup['evidence_dir'] / 'attempt-01-E-initial.json').read_text() == 'prior evidence'
    assert calls == []
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 0
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 0


def test_slow_global_reservation_does_not_get_a_fresh_dispatch_deadline(setup, monkeypatch):
    now = [100.0]
    monkeypatch.setattr(evaluation.time, 'monotonic', lambda: now[0])
    reserve = ModelBudget.reserve
    def slow_reserve(self, **kwargs):
        reserve(self, **kwargs)
        now[0] += 61
    monkeypatch.setattr(ModelBudget, 'reserve', slow_reserve)
    calls = []
    result = run(setup, calls)
    assert result['errorCode'] == 9 and result['latencySeconds'] == 61
    assert result['globalReservationCompleted'] is True and result['providerAttemptStarted'] is False
    assert calls == []
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 1


def test_existing_four_smoke_limit_is_preserved_while_evaluation_uses_normal_reservation(setup):
    ledger = ModelBudget(setup['settings'].model_budget_path)
    for _ in range(4): ledger.reserve(live_check=True)
    with pytest.raises(BudgetFailure): ledger.reserve(live_check=True)
    assert ledger.read()['attempts'] == ledger.read()['liveChecks'] == 4
    assert run(setup)['errorCode'] == 0
    assert ledger.read()['attempts'] == 5 and ledger.read()['liveChecks'] == 4
    with pytest.raises(BudgetFailure): ledger.reserve(live_check=True)


@pytest.mark.parametrize('stage', ['serialize', 'fsync', 'publish'])
def test_json_publication_failure_never_exposes_partial_final_or_cleans_other_files(tmp_path, monkeypatch, stage):
    destination = tmp_path / 'evidence.json'
    unrelated = tmp_path / '.someone-else.tmp'
    unrelated.write_text('preserve')
    value = {'item': object()} if stage == 'serialize' else {'item': 'complete'}
    if stage == 'fsync':
        monkeypatch.setattr(evaluation.os, 'fsync', lambda *_: (_ for _ in ()).throw(OSError()))
    if stage == 'publish':
        monkeypatch.setattr(evaluation, 'publish_new', lambda *_: (_ for _ in ()).throw(OSError()))
    with pytest.raises((TypeError, OSError)):
        evaluation.write_json_exclusive(destination, value)
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == [unrelated]
    assert unrelated.read_text() == 'preserve'


def test_atomic_json_publication_is_complete_and_never_replaces(tmp_path, monkeypatch):
    destination = tmp_path / 'evidence.json'
    original_publish = evaluation.publish_new
    def checked(temporary, final):
        assert not final.exists()
        assert json.loads(temporary.read_text(encoding='utf-8')) == {'text': 'complete æøå'}
        original_publish(temporary, final)
    monkeypatch.setattr(evaluation, 'publish_new', checked)
    evaluation.write_json_exclusive(destination, {'text': 'complete æøå'})
    original = destination.read_bytes()
    monkeypatch.setattr(evaluation, 'publish_new', original_publish)
    with pytest.raises(OSError):
        evaluation.write_json_exclusive(destination, {'replacement': True})
    assert destination.read_bytes() == original
    assert list(tmp_path.iterdir()) == [destination]


def test_post_dispatch_evidence_failure_keeps_both_allowances(setup, monkeypatch):
    def fail(*_): raise OSError('PRIVATE_FILESYSTEM_ERROR')
    monkeypatch.setattr(evaluation, 'write_json_exclusive', fail)
    calls = []
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        run(setup, calls)
    assert failure.value.code == 6 and len(calls) == 1
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 1
    assert not list(setup['evidence_dir'].glob('attempt-*.json'))


def test_registration_failure_cleans_owned_staging_and_can_be_retried(tmp_path, registered, monkeypatch):
    data, _ = registered
    evidence = tmp_path / 'evidence'
    destination = evaluation.registration_directory(data, evidence)
    publish = evaluation.publish_new
    seen = []
    def fail_directory(temporary, final, **kwargs):
        if kwargs.get('directory'):
            assert not destination.exists()
            assert {path.name for path in temporary.iterdir()} == {'registration.json', 'source-c.pdf'}
            seen.append(temporary)
            raise OSError()
        return publish(temporary, final, **kwargs)
    monkeypatch.setattr(evaluation, 'publish_new', fail_directory)
    with pytest.raises(OSError): evaluation.register(data, evidence)
    assert not destination.exists() and all(not path.exists() for path in seen)
    monkeypatch.setattr(evaluation, 'publish_new', publish)
    evaluation.register(data, evidence)
    evaluation.verify_registration(data, evidence)
    old = (destination / 'registration.json').read_bytes()
    with pytest.raises(OSError): evaluation.register(data, evidence)
    assert (destination / 'registration.json').read_bytes() == old
    assert list(evidence.iterdir()) == [destination]


@pytest.mark.parametrize('artifact,limit', [('registration.json', 100_000), ('source-c.pdf', 1_000_000)])
def test_registration_artifact_reads_are_bounded_before_allocation(setup, monkeypatch, artifact, limit):
    original_open = Path.open
    requested = []
    class Oversized:
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self, count=-1):
            assert count == limit + 1
            requested.append(count)
            return b'x' * count
    def bounded_open(path, *args, **kwargs):
        if path.name == artifact:
            return Oversized()
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', bounded_open)
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        evaluation.verify_registration(setup['data'], setup['evidence_dir'])
    assert failure.value.code == 7 and requested == [limit + 1]


def test_stable_rubric_threshold_changes_registration_but_mutable_results_do_not(tmp_path, monkeypatch, registered):
    original_text = evaluation.RUBRIC_PATH.read_text(encoding='utf-8')
    rubric = tmp_path / 'rubric.md'
    monkeypatch.setattr(evaluation, 'RUBRIC_PATH', rubric)
    rubric.write_text(original_text.replace('five approved live cases executed and assessed', 'mutable status'), encoding='utf-8')
    same, _ = evaluation.registration()
    assert same['rubricSha256'] == registered[0]['rubricSha256']
    rubric.write_text(original_text.replace('at least four of five concepts covered', 'at least five of five concepts covered'), encoding='utf-8')
    changed, _ = evaluation.registration()
    assert changed['rubricSha256'] != same['rubricSha256']
    assert changed['registrationFingerprint'] != same['registrationFingerprint']
    assert changed['corpusFingerprint'] == same['corpusFingerprint']


def test_unexpected_internal_bug_gets_numeric_internal_error(setup, monkeypatch):
    def broken(*_): raise RuntimeError('PRIVATE_INTERNAL_BUG')
    monkeypatch.setattr(evaluation, 'resolve', broken)
    result = run(setup)
    assert result['errorCode'] == 10
    assert result['globalReservationCompleted'] is True and result['providerAttemptStarted'] is True
    assert 'PRIVATE_INTERNAL_BUG' not in json.dumps(result)


def test_explicit_cancellation_retains_allowances_safe_evidence_and_releases_lock(setup):
    async def scenario():
        entered = asyncio.Event()
        async def held(_):
            entered.set()
            await asyncio.Event().wait()
        task = asyncio.create_task(evaluation.run_case('E', **setup, transport=httpx.MockTransport(held)))
        await asyncio.wait_for(entered.wait(), 2)
        task.cancel()
        result = await asyncio.wait_for(task, 2)
        assert result['errorCode'] == 11
        assert result['globalReservationCompleted'] is True and result['providerAttemptStarted'] is True
        assert 'output' not in result
        saved = json.loads((setup['evidence_dir'] / 'attempt-01-E-initial.json').read_text())
        assert saved == result
    asyncio.run(scenario())
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 1
    grant = evaluation.EvaluationGrant(setup['grant_path'])
    assert grant.read()['attempts'] == 1
    with grant.exclusive(): pass


@pytest.mark.parametrize('release', ['normal', 'terminate'])
def test_subprocess_grant_exclusion_and_owned_child_release(tmp_path, release):
    path = tmp_path / 'grant.json'
    evaluation.EvaluationGrant.initialize(path)
    script = '''import sys
from scripts.content_evaluation import EvaluationGrant
with EvaluationGrant(sys.argv[1]).claim():
    print('locked', flush=True)
    sys.stdin.readline()
'''
    child = subprocess.Popen([sys.executable, '-c', script, str(path)], cwd=evaluation.ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ready = threading.Event()
    lines = []
    reader = threading.Thread(target=lambda: (lines.append(child.stdout.readline()), ready.set()), daemon=True)
    reader.start()
    try:
        assert ready.wait(5) and lines == ['locked\n']
        with pytest.raises(BudgetFailure):
            with evaluation.EvaluationGrant(path).claim(): pass
        if release == 'normal':
            child.stdin.write('\n'); child.stdin.flush()
        else:
            child.terminate()
        child.wait(timeout=5)
        grant = evaluation.EvaluationGrant(path)
        with grant.claim() as attempt:
            assert attempt == 2
    finally:
        if child.poll() is None:
            child.terminate()
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill(); child.wait(timeout=5)
        for stream in (child.stdin, child.stdout, child.stderr): stream.close()
        reader.join(timeout=1)


@pytest.mark.parametrize('case,phase', [(case, phase) for case in evaluation.CASES for phase in ('initial', 'recheck')])
def test_selected_live_cli_routes_exact_case_phase_to_real_temporary_runner(setup, monkeypatch, capsys, case, phase):
    monkeypatch.setattr(evaluation, 'registration', lambda: (setup['data'], setup['accepted']))
    monkeypatch.setattr(evaluation.Settings, 'from_env', lambda: setup['settings'])
    real_run = evaluation.run_case
    calls = []
    async def temporary_run(selected, **kwargs):
        return await real_run(selected, **kwargs, grant_path=setup['grant_path'],
            evidence_dir=setup['evidence_dir'], transport=transport(calls))
    monkeypatch.setattr(evaluation, 'run_case', temporary_run)
    assert evaluation.main(['--live', '--case', case, '--phase', phase]) == 0
    assert json.loads(capsys.readouterr().out)['case'] == case
    assert len(calls) == 1
    assert calls[0] == json.loads(evaluation.request_bytes(setup['accepted'][case]))
    saved = json.loads((setup['evidence_dir'] / f'attempt-01-{case}-{phase}.json').read_text())
    assert saved['case'] == case and saved['phase'] == phase


@pytest.mark.parametrize('case', evaluation.CASES)
def test_committed_assessment_integrity_links_and_enumeration_only(case):
    """Traceability checks, never an automated judgment of semantic correctness."""
    directory = evaluation.EVIDENCE_DIR
    assessment = json.loads((directory / f'assessment-{case}.json').read_text(encoding='utf-8'))
    raw = (directory / assessment['observation']).read_bytes()
    assert evaluation.digest(raw) == assessment['observationSha256']
    observation = json.loads(raw)
    registration_path = evaluation.registration_directory(observation, directory) / 'registration.json'
    registration = json.loads(registration_path.read_text(encoding='utf-8'))
    assert assessment['case'] == observation['case'] == case
    for key in ('corpusFingerprint', 'promptSha256'):
        assert assessment[key] == observation[key] == registration[key]
    source = {unit['id']: unit for unit in registration['cases'][case]['sourceUnits']}
    output = observation['output']
    expected = [(part, position, item['id']) for part in evaluation.PARTS
                for position, item in enumerate(output[part], 1)]
    assert [(item['part'], item['position'], item['itemId']) for item in assessment['items']] == expected
    by_id = {item['id']: item for part in evaluation.PARTS for item in output[part]}
    for item_audit in assessment['items']:
        item = by_id[item_audit['itemId']]
        assert item_audit['questionOrTerm'] == item.get('question', item.get('term'))
        assert item_audit['checkedReferenceLabels'] == [ref['label'] for ref in item['references']]
        text = item.get('text', item.get('explanation', item.get('answer')))
        cursor = 0
        supported_ids = set()
        for claim in item_audit['claims']:
            excerpt = claim['exactOutputExcerpt']
            position = text.index(excerpt, cursor)
            assert not text[cursor:position].strip()
            cursor = position + len(excerpt)
            for support in claim['support']:
                unit = source[support['sourceUnitId']]
                assert support['location'] == unit['location']
                assert support['exactSourceExcerpt'] in unit['text']
                supported_ids.add(unit['id'])
        assert not text[cursor:].strip()
        assert supported_ids == {ref['sourceUnitId'] for ref in item['references']}
        for ref in item['references']:
            unit = source[ref['sourceUnitId']]
            assert ref['label'] == f"{'Side' if unit['kind'] == 'page' else 'Avsnitt'} {unit['location']}"
    concepts = registration['cases'][case]['concepts']
    assert [entry['conceptId'] for entry in assessment['coverage']] == [entry['id'] for entry in concepts]
    for coverage, concept in zip(assessment['coverage'], concepts):
        assert coverage['requiredMeaning'] == concept['meaning']
        assert coverage['sourceLocation'] == concept['location']
        item = by_id[coverage['itemId']]
        assert coverage['exactOutputExcerpt'] in item.get('text', item.get('explanation', item.get('answer')))
    assert assessment['qualificationsChecked'] == output['insufficiency']
    assert assessment['warningsChecked'] == output['warnings']
