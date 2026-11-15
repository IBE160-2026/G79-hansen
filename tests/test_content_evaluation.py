"""Offline evaluation controls; no real keys, ledgers, grants or provider calls."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import json

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


def test_evidence_write_failure_keeps_both_reservations(setup):
    (setup['evidence_dir'] / 'attempt-01-E-initial.json').write_text('prior evidence')
    with pytest.raises(evaluation.EvaluationFailure) as failure:
        run(setup)
    assert failure.value.code == 6
    assert (setup['evidence_dir'] / 'attempt-01-E-initial.json').read_text() == 'prior evidence'
    assert evaluation.EvaluationGrant(setup['grant_path']).read()['attempts'] == 1
    assert ModelBudget(setup['settings'].model_budget_path).read()['attempts'] == 1


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
