"""Explicit approved synthetic smoke only; prints content-free observations.

Requires process MODEL_ENABLED, OPENAI_API_KEY and MODEL_BUDGET_PATH. Never
initializes/resets a ledger and never retries. At most four automated checks are
allowed over this ledger's lifetime, including failed or uncertain requests.
"""
import argparse
import asyncio
import base64
import importlib.util
import json
from pathlib import Path
import time

from app.adapters.model import OpenAIModel, ModelFailure, request_bytes
from app.adapters.pdf import extract_pdf
from app.config import Settings
from app.contracts.sources import ExtractRequest
from app.services.extraction import extract_pdf_result, extract_text, prepare
from app.services.generation import resolve
from app.services.model_budget import ModelBudget


def sources(selected=None):
    statements = ('Water can be solid, liquid or gas. Freezing changes liquid water to solid ice.',
                  'Evaporation changes liquid water to gas. Condensation changes water gas to liquid.')
    for name, language, detail, text in (
        ('nb-short', 'nb', 'short', '\n\n'.join(statements)),
        ('en-detailed', 'en', 'detailed', '\n\n'.join(statements)),
        ('insufficient', 'en', 'short', '...')):
        if selected and selected != name:
            continue
        request = ExtractRequest(schemaVersion='1.0', workspaceId='synthetic-smoke-workspace',
            clientRevision=0, commandSequence=1, kind='paste', text=text,
            settings={'language': language, 'detail': detail, 'subject': ''})
        yield name, extract_text(request, prepare(request))
    # Exercise the same contained extractor with a synthetic, four-physical-page
    # PDF. Only readable text from pages 1 and 3 reaches the model.
    if selected and selected != 'pdf-physical-gaps':
        return
    path = Path(__file__).resolve().parents[1] / 'tests' / 'pdf_fixtures.py'
    spec = importlib.util.spec_from_file_location('smoke_pdf_fixtures', path)
    fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
    content = fixture.make_pdf([statements[0], None, statements[1], None], image_pages=(4,))
    request = ExtractRequest(schemaVersion='1.0', workspaceId='synthetic-smoke-workspace',
        clientRevision=0, commandSequence=1, kind='pdf', contentBase64=base64.b64encode(content).decode(),
        settings={'language': 'nb', 'detail': 'short', 'subject': ''})
    yield 'pdf-physical-gaps', extract_pdf_result(request, extract_pdf(content))


async def run(selected):
    settings = Settings.from_env()
    if not settings.model_available:
        raise ValueError('configuration')
    ledger = ModelBudget(settings.model_budget_path)
    adapter = OpenAIModel(settings)
    observations = []
    # Source extraction/preflight precedes each reservation, including PDF work.
    for name, accepted in sources(selected):
        body = request_bytes(accepted)
        ledger.reserve(live_check=True)
        ledger.check_dispatch()
        started = time.monotonic()
        try:
            try:
                async with asyncio.timeout(60):
                    completion = await adapter.complete(body)
            except ModelFailure as failure:
                if failure.usage is not None:
                    ledger.observe(*failure.usage)
                raise
            ledger.observe(completion.input_tokens, completion.output_tokens)
            bundle = resolve(accepted, completion.output)
            labels = sorted({reference.label for part in ('summary', 'concepts', 'flashcards', 'quiz')
                             for item in getattr(bundle, part) for reference in item.references})
            counts = {part: len(getattr(bundle, part)) for part in ('summary', 'concepts', 'flashcards', 'quiz')}
            observation = {'case': name, 'status': 'validated', 'model': completion.model,
                'latencySeconds': round(time.monotonic() - started, 3),
                'inputTokens': completion.input_tokens, 'outputTokens': completion.output_tokens,
                'estimatedUsd': round((completion.input_tokens * .1 + completion.output_tokens * .5) / 1_000_000, 8),
                'sectionCounts': counts, 'references': labels, 'sourceLocations': [u.location for u in accepted.source.units],
                'unreadablePages': accepted.unreadable_pages}
            if name == 'insufficient':
                observation['allSectionsInsufficient'] = all(count == 0 for count in counts.values())
            observations.append(observation)
            print(json.dumps(observation, sort_keys=True), flush=True)
        except Exception:
            # Provider errors/payloads, credentials and generated prose stay private.
            print(json.dumps({'case': name, 'status': 'failed',
                              'latencySeconds': round(time.monotonic() - started, 3)}), flush=True)
            raise RuntimeError('smoke failed') from None
    print(json.dumps({'ledger': ledger.read()}, sort_keys=True), flush=True)
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('nb-short', 'en-detailed', 'insufficient', 'pdf-physical-gaps'))
    args = parser.parse_args()
    try:
        asyncio.run(run(args.case))
    except Exception:
        parser.exit(1, 'Synthetic smoke stopped safely; no automatic retry or reservation refund.\n')


if __name__ == '__main__':
    main()
