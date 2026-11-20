"""Opt-in prediction evidence archive; never a publication receipt."""
import gzip
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path


def clean(value):
    if hasattr(value, 'to_json') and hasattr(value, 'columns'):
        return json.loads(value.to_json(orient='records', date_format='iso'))
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, 'item'):
        return clean(value.item())
    return value


def archive(sport, stage, run_id, inputs):
    """Only explicitly supplied model data is saved; never inspect env or clients."""
    directory = os.getenv(sport + '_AUDIT_DIR', '')
    if not directory:
        return None
    payload = {
        'schema': 'sports-accuracy-inputs-v1', 'sport': sport,
        'stage': stage, 'run_id': run_id,
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'commit': os.getenv('GITHUB_SHA', ''),
        'run_attempt': os.getenv('GITHUB_RUN_ATTEMPT', ''),
        'publication_receipt': False,
        'limitations': 'Captured inputs only; missing context is not inferred. Replay must check event and quote times.',
        'inputs': clean(inputs),
    }
    path = Path(directory) / (stage + '.json.gz')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with gzip.open(temporary, 'wt', encoding='utf-8') as handle:
        json.dump(payload, handle, default=str, allow_nan=False)
    temporary.replace(path)
    print(f'Audit inputs archived: {stage}')
    return path

