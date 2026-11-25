"""Teaching prototype. Not a security sandbox or production approval service."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def snapshot(root):
    result = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            result[str(path.relative_to(root))] = 'SYMLINK'
        elif path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def allowed_diff(before, after, allowed):
    changed = sorted(k for k in before.keys() | after.keys()
                     if before.get(k) != after.get(k))
    return changed, set(changed) <= set(allowed) and all(
        after.get(k) != 'SYMLINK' for k in changed)


def command(provider, prompt):
    if provider == 'codex':
        return ['codex', '--ask-for-approval', 'never', 'exec', '--sandbox', 'workspace-write', prompt]
    if provider == 'claude':
        return ['claude', '-p', '--permission-mode', 'dontAsk', prompt]
    raise ValueError('unknown provider')


def verify(candidate, trusted):
    # Run only the copied candidate module and trusted tests in a fresh directory.
    # This is test separation, NOT isolation from arbitrary Python execution.
    with tempfile.TemporaryDirectory() as directory:
        check = Path(directory)
        shutil.copyfile(candidate / 'pricing.py', check / 'pricing.py')
        shutil.copyfile(trusted, check / 'test_pricing.py')
        try:
            result = subprocess.run([sys.executable, '-B', '-m', 'unittest', '-q'],
                                    cwd=check, timeout=15, capture_output=True)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False


def execute(provider, root, task, trusted, invoke=None):
    if set(task) != {'id','objective','allowed_paths','max_attempts','timeout_seconds','acceptance','approval_required'}:
        raise ValueError('invalid task keys')
    if task['allowed_paths'] != ['pricing.py'] or task['approval_required'] is not True:
        raise ValueError('invalid task policy')
    if type(task['max_attempts']) is not int or not 1 <= task['max_attempts'] <= 3:
        raise ValueError('invalid retry budget')
    if type(task['timeout_seconds']) is not int or not 1 <= task['timeout_seconds'] <= 300:
        raise ValueError('invalid timeout')
    before = snapshot(root)
    events = []
    for attempt in range(1, task['max_attempts'] + 1):
        start = time.monotonic()
        try:
            if invoke is not None:
                code = invoke(root)
            elif provider == 'mock':
                # The mock exercises the controller without using a model.
                code = 0
            else:
                prompt = json.dumps(task) + '\nModify only pricing.py; no commits. Verify requirements.'
                # No shell interpolation. External process-tree isolation is required.
                code = subprocess.run(command(provider, prompt), cwd=root,
                                      timeout=task['timeout_seconds'],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        except (OSError, subprocess.TimeoutExpired):
            return {'status':'execution_failed','events':events}
        changed, scoped = allowed_diff(before, snapshot(root), task['allowed_paths'])
        event = {'attempt':attempt, 'exit_code':code, 'changed':changed,
                 'seconds':round(time.monotonic()-start,3), 'scope_ok':scoped}
        events.append(event)
        if not scoped:
            return {'status':'scope_denied','events':events}
        if code != 0:
            return {'status':'execution_failed','events':events}
        event['verified'] = verify(root, trusted)
        if event['verified']:
            return {'status':'awaiting_human_review','events':events,
                    'candidate_sha256':snapshot(root).get('pricing.py')}
    return {'status':'verification_failed','events':events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=['mock','codex','claude'], default='mock')
    parser.add_argument('--workspace', type=Path, required=True)
    args = parser.parse_args()
    target = args.workspace.resolve()
    if target.exists():
        parser.error('workspace must not already exist')
    target.mkdir(parents=True)
    for name in ['pricing.py','AGENTS.md','CLAUDE.md','.codex','.claude']:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, target / name)
        else:
            shutil.copyfile(source, target / name)
    # Initialize a disposable repo; agent never receives a push credential here.
    subprocess.run(['git','init','-q',str(target)], check=True)
    # Git metadata changes are intentionally rejected by postcondition.
    task = json.loads((ROOT / 'task.json').read_text())
    result = execute(args.provider, target, task, ROOT / 'trusted/test_pricing.py')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'awaiting_human_review' else 1

if __name__ == '__main__':
    raise SystemExit(main())
