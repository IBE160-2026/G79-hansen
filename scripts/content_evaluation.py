"""Registered synthetic quality evaluation; offline unless --live is explicit.

No arbitrary sources, account operations, hidden retries, model judges or budget
initialization. Errors expose numeric codes only. Semantic assessment is manual.
"""
import argparse
import asyncio
from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from threading import Lock
import time
from uuid import uuid4

from pydantic import ValidationError

from app.adapters.model import INSTRUCTIONS, MODEL, ModelFailure, OpenAIModel, request_bytes
from app.config import Settings
from app.services.generation import resolve
from app.services.model_budget import BudgetFailure, ModelBudget
from app.services.receipts import canonical

ROOT = Path(__file__).resolve().parents[1]
GRANT_PATH = ROOT / '.model-budget-evaluation-2-6.json'
EVIDENCE_DIR = ROOT / '.docs' / 'implementation-artifacts' / 'content-evaluation-evidence'
CASES = ('A', 'B', 'C', 'D', 'E')
PARTS = ('summary', 'concepts', 'flashcards', 'quiz')
DEADLINE_SECONDS = 60
RUBRIC_PATH = ROOT / '.docs' / 'implementation-artifacts' / 'content-evaluation.md'


def fixtures():
    name = '_registered_content_fixtures_2_6'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT / 'tests' / 'content_fixtures.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


class EvaluationFailure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class EvaluationGrant(ModelBudget):
    """Separate, content-free eight-attempt cap; the global ledger still rules.

    The OS lock is held throughout dispatch and evidence persistence. A second
    process or thread fails immediately. Never recreates a missing grant.
    """
    def __init__(self, path):
        super().__init__(path)
        self.running = Lock()

    @staticmethod
    def initial():
        return {'version': 1, 'maximumAttempts': 8, 'reservationMicrousd': 50_000, 'attempts': 0}

    @classmethod
    def initialize(cls, path):
        with Path(path).open('x', encoding='ascii') as target:
            target.write(json.dumps(cls.initial(), sort_keys=True))
            target.flush()
            os.fsync(target.fileno())
        if os.name != 'nt':
            descriptor = os.open(Path(path).parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)

    def read(self):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError()
                result[key] = value
            return result
        try:
            if self.path.stat().st_size > 512:
                raise ValueError()
            value = json.loads(self.path.read_text(encoding='ascii'), object_pairs_hook=unique)
            expected = self.initial()
            if (type(value) is not dict or set(value) != set(expected) or
                    any(type(value[key]) is not int for key in expected) or
                    any(value[key] != expected[key] for key in expected if key != 'attempts') or
                    not 0 <= value['attempts'] <= 8):
                raise ValueError()
            return value
        except (OSError, ValueError, TypeError, UnicodeError):
            raise BudgetFailure() from None

    @contextmanager
    def claim(self, preflight=lambda _attempt: None):
        if not self.running.acquire(blocking=False):
            raise BudgetFailure()
        try:
            with self.exclusive():
                value = self.read()
                if value['attempts'] >= 8:
                    raise BudgetFailure()
                preflight(value['attempts'] + 1)
                value['attempts'] += 1
                self.write(value)
                yield value['attempts']
        finally:
            self.running.release()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_bounded(path, limit):
    with Path(path).open('rb') as source:
        value = source.read(limit + 1)
    if len(value) > limit:
        raise ValueError()
    return value


def rubric_prose(text):
    text = text.replace('\r\n', '\n')
    section = text.split('## Assessment and acceptance\n', 1)[1]
    before, after = section.split('| Case | Semantic support |', 1)
    paragraph = after.split('Maintain a separate defect table', 1)[1].split('\n\n', 1)[0]
    return before.strip() + '\n\n' + ('Maintain a separate defect table' + paragraph).strip() + '\n'


def registration():
    """Preflight all registered sources using production extraction, no config IO."""
    corpus = fixtures()
    accepted = {case: corpus.accepted_case(case) for case in CASES}
    cases = {}
    for case, source in accepted.items():
        concepts = corpus.CONCEPTS.get('A' if case == 'D' else case, ())
        cases[case] = {'kind': source.kind, 'settings': source.settings.model_dump(by_alias=True),
            'sourceUnits': [unit.model_dump(by_alias=True) for unit in source.source.units],
            'totalPages': source.total_pages, 'unreadablePages': source.unreadable_pages,
            'concepts': [asdict(concept) for concept in concepts],
            'requestSha256': digest(request_bytes(source))}
    pdf = corpus.readable_pdf()
    corpus_data = {'revision': corpus.REVISION, 'cases': cases,
        'pdfSha256': digest(pdf), 'pdfVisibleLines': corpus.pdf_lines()}
    # Persist neither random source/generation identity nor proof/receipt fields.
    files = ('tests/content_fixtures.py', 'scripts/content_evaluation.py',
        'app/adapters/model.py', 'app/adapters/pdf.py', 'scripts/pdf_probe.py',
        'app/services/extraction.py', 'app/services/generation.py', 'app/services/model_budget.py',
        'app/contracts/learning.py', 'app/contracts/generation.py', 'app/contracts/sources.py')
    hashes = {name: digest((ROOT / name).read_bytes()) for name in files}
    # A prompt/code correction creates a new registration, never a new corpus.
    frozen_corpus = {**corpus_data, 'cases': {case: {key: value for key, value in details.items()
        if key != 'requestSha256'} for case, details in cases.items()}}
    result = {**corpus_data, 'corpusFingerprint': digest(canonical(frozen_corpus)),
        'rubricSha256': digest(rubric_prose(read_bounded(RUBRIC_PATH, 128_000).decode('utf-8')).encode('utf-8')),
        'promptSha256': digest(INSTRUCTIONS.encode('utf-8')), 'implementationFiles': hashes,
        'implementationFingerprint': digest(canonical(hashes)), 'model': MODEL,
        'bounds': {'deadlineSeconds': 60, 'maxOutputTokens': 8000, 'maxProviderBytes': 262144,
                   'reservationMicrousd': 50000, 'maximumEvaluationAttempts': 8},
        'semanticAssessment': 'pending'}
    result['registrationFingerprint'] = digest(canonical(result))
    return result, accepted


def registration_directory(data, evidence_dir):
    return Path(evidence_dir) / ('registration-' + data['registrationFingerprint'])


def sync_directory(directory):
    if os.name != 'nt':
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def publish_new(temporary, destination, *, directory=False):
    """Atomic no-replace publication; Windows write-through / POSIX dir fsync."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        move = ctypes.WinDLL('kernel32', use_last_error=True).MoveFileExW
        move.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
        move.restype = wintypes.BOOL
        if not move(str(temporary.resolve()), str(destination.absolute()), 0x8):
            raise ctypes.WinError(ctypes.get_last_error())
    elif directory:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        if sys.platform.startswith('linux'):
            rename = libc.renameat2
            rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
            result = rename(-100, os.fsencode(temporary), -100, os.fsencode(destination), 1)
        elif sys.platform == 'darwin':
            rename = libc.renamex_np
            rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
            result = rename(os.fsencode(temporary), os.fsencode(destination), 4)
        else:
            raise OSError('atomic exclusive directory publication unavailable')
        if result:
            raise OSError(ctypes.get_errno(), 'exclusive directory publication failed')
    else:
        os.link(temporary, destination)
        temporary.unlink()
    sync_directory(destination.parent)


def write_json_exclusive(path, value):
    path = Path(path)
    temporary = path.with_name('.' + path.name + '.' + uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8', newline='\n') as target:
            json.dump(value, target, ensure_ascii=False, indent=2, sort_keys=True)
            target.write('\n')
            target.flush()
            os.fsync(target.fileno())
        publish_new(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def register(data, evidence_dir=EVIDENCE_DIR):
    directory = registration_directory(data, evidence_dir)
    directory.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.registration-', dir=directory.parent))
    try:
        write_json_exclusive(temporary / 'registration.json', data)
        with (temporary / 'source-c.pdf').open('xb') as target:
            target.write(fixtures().readable_pdf())
            target.flush()
            os.fsync(target.fileno())
        sync_directory(temporary)
        publish_new(temporary, directory, directory=True)
    finally:
        # Only this call's randomly named owned directory can be removed.
        if temporary.exists():
            if temporary.resolve().parent != directory.parent.resolve() or not temporary.name.startswith('.registration-'):
                raise OSError('owned temporary directory boundary mismatch')
            shutil.rmtree(temporary)
    return directory


def verify_registration(data, evidence_dir):
    directory = registration_directory(data, evidence_dir)
    try:
        raw = read_bounded(directory / 'registration.json', 100_000)
        if json.loads(raw) != data:
            raise ValueError()
        if digest(read_bounded(directory / 'source-c.pdf', 1_000_000)) != data['pdfSha256']:
            raise ValueError()
    except (OSError, ValueError, TypeError):
        raise EvaluationFailure(7) from None


def project(bundle):
    """Whitelist resolved synthetic learning text only, never dump a response."""
    result = {}
    fields = {'summary': ('text',), 'concepts': ('term', 'explanation'),
              'flashcards': ('question', 'answer'), 'quiz': ('question', 'answer')}
    for part, names in fields.items():
        result[part] = []
        for item in getattr(bundle, part):
            result[part].append({'id': item.id, **{name: getattr(item, name) for name in names},
                'references': [{'sourceUnitId': ref.source_unit_id, 'label': ref.label} for ref in item.references]})
    result['warnings'] = list(bundle.warnings)
    result['insufficiency'] = {part: getattr(bundle.insufficiency, part) for part in PARTS}
    return result


async def run_case(case, *, settings, data, accepted, grant_path=GRANT_PATH,
                   evidence_dir=EVIDENCE_DIR, transport=None, phase='initial'):
    """One fixed case; injected transport/temporary paths support offline tests."""
    started = time.monotonic()
    deadline = started + DEADLINE_SECONDS

    def remaining():
        seconds = deadline - time.monotonic()
        if seconds <= 0:
            raise TimeoutError()
        return seconds

    if case not in CASES or phase not in ('initial', 'recheck'):
        raise EvaluationFailure(8)
    if not settings.model_available:
        raise EvaluationFailure(1)
    verify_registration(data, evidence_dir)
    body = request_bytes(accepted[case])
    if digest(body) != data['cases'][case]['requestSha256']:
        raise EvaluationFailure(7)
    grant = EvaluationGrant(grant_path)
    ledger = ModelBudget(settings.model_budget_path)
    adapter = OpenAIModel(settings, transport=transport)
    def destination_for(attempt):
        return Path(evidence_dir) / f'attempt-{attempt:02d}-{case}-{phase}.json'

    def preflight_destination(attempt):
        try:
            destination_for(attempt).lstat()
        except FileNotFoundError:
            return
        except OSError:
            pass
        raise EvaluationFailure(6)
    # Grant first, global reservation second. Failures at either stage never
    # refund previous durable state. Lock remains held until all cleanup exits.
    try:
        try:
            remaining()
        except TimeoutError:
            raise EvaluationFailure(9) from None
        with grant.claim(preflight_destination) as attempt:
            observation = {'case': case, 'phase': phase, 'grantAttempt': attempt,
                'registrationFingerprint': data['registrationFingerprint'],
                'corpusFingerprint': data['corpusFingerprint'],
                'implementationFingerprint': data['implementationFingerprint'],
                'promptSha256': data['promptSha256'], 'model': MODEL,
                'rubricSha256': data['rubricSha256'],
                'settings': data['cases'][case]['settings'],
                'globalReservationCompleted': False, 'providerAttemptStarted': False,
                'status': 'failed', 'errorCode': 3, 'semanticAssessment': 'pending'}
            try:
                remaining()
                ledger.reserve()
                observation['globalReservationCompleted'] = True
                ledger.check_dispatch()
                # Synchronous durable IO retains its cleanup ownership. Its
                # elapsed time never buys a fresh provider deadline afterward.
                seconds = remaining()
                observation['errorCode'] = 4
                async with asyncio.timeout(seconds):
                    try:
                        observation['providerAttemptStarted'] = True
                        completion = await adapter.complete(body)
                    except ModelFailure as failure:
                        if failure.usage is not None:
                            if all(type(n) is int for n in failure.usage):
                                observation['inputTokens'], observation['outputTokens'] = failure.usage
                            ledger.observe(*failure.usage)
                            observation['estimatedUsd'] = round((failure.usage[0] * .1 + failure.usage[1] * .5) / 1_000_000, 8)
                        raise
                    observation.update(inputTokens=completion.input_tokens, outputTokens=completion.output_tokens)
                    ledger.observe(completion.input_tokens, completion.output_tokens)
                    remaining()
                    observation['estimatedUsd'] = round((completion.input_tokens * .1 + completion.output_tokens * .5) / 1_000_000, 8)
                    observation['errorCode'] = 5
                    if completion.model != MODEL:
                        raise ModelFailure()
                    bundle = resolve(accepted[case], completion.output)
                    remaining()
                    observation.update(status='structurally_validated', errorCode=0, output=project(bundle))
            except TimeoutError:
                observation['errorCode'] = 9
            except asyncio.CancelledError:
                observation['errorCode'] = 11
            except BudgetFailure:
                observation['errorCode'] = 4 if observation['providerAttemptStarted'] else 3
            except (ModelFailure, ValidationError):
                observation['errorCode'] = 5 if observation['errorCode'] == 5 else 4
            except Exception:
                observation['errorCode'] = 10
            observation['latencySeconds'] = round(time.monotonic() - started, 3)
            destination = destination_for(attempt)
            try:
                write_json_exclusive(destination, observation)
            except (OSError, ValueError, TypeError):
                raise EvaluationFailure(6) from None
            return observation
    except BudgetFailure:
        raise EvaluationFailure(2) from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--live', action='store_true', help='one explicitly selected approved case')
    action.add_argument('--register', action='store_true', help='write immutable synthetic preflight evidence offline')
    action.add_argument('--initialize-grant', action='store_true', help='exclusive-create approved allowance once; no dispatch')
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--phase', choices=('initial', 'recheck'), default='initial')
    args = parser.parse_args(argv)
    try:
        if args.initialize_grant:
            EvaluationGrant.initialize(GRANT_PATH)
            print(json.dumps({'statusCode': 0, 'maximumAttempts': 8}))
            return 0
        data, accepted = registration()
        if args.register:
            register(data)
        if not args.live:
            print(json.dumps({'statusCode': 0, 'offline': True,
                'registrationFingerprint': data['registrationFingerprint'],
                'corpusFingerprint': data['corpusFingerprint'], 'caseCount': len(accepted),
                'sourceLocations': {case: [u.location for u in source.source.units] for case, source in accepted.items()}}))
            return 0
        if args.case is None:
            raise EvaluationFailure(8)
        observation = asyncio.run(run_case(args.case, settings=Settings.from_env(), data=data,
            accepted=accepted, phase=args.phase))
        print(json.dumps({key: observation[key] for key in ('case', 'grantAttempt', 'status', 'errorCode', 'latencySeconds')}))
        return int(observation['errorCode'] != 0)
    except EvaluationFailure as failure:
        print(json.dumps({'statusCode': failure.code}))
    except (Exception, KeyboardInterrupt):
        print(json.dumps({'statusCode': 10}))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
