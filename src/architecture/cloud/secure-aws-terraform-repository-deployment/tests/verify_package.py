#!/usr/bin/env python3
"""Static package conformance smoke checks; not a replacement for terraform validate."""
from pathlib import Path
import csv
import re
import sys
try:
    import yaml
except ImportError as e:
    raise SystemExit('PyYAML required for tests: pip install pyyaml') from e
ROOT = Path(__file__).resolve().parents[1]
issues=[]

def require(cond,msg):
    if not cond: issues.append(msg)

main=(ROOT/'standard/aws-terraform-repository-deployment-standard.tex').read_text()
for match in re.findall(r'\\(?:input|lstinputlisting)(?:\[[^]]*\])?\{([^}]+)\}',main):
    require((ROOT/'standard'/match).exists(),f'Unresolved LaTeX include {match}')
for match in re.findall(r'\\inputminted(?:\[[^]]*\])?\{[^}]+\}\{([^}]+)\}', main):
    require((ROOT/'standard'/match).exists(), f'Unresolved code include {match}')
for env in ('dev','test','prod'):
    root=ROOT/f'examples/terraform/application/environments/{env}'
    backend=(root/'backend.tf').read_text()
    require(f'applications/sample-app/{env}/terraform.tfstate' in backend,f'{env} state key missing')
    require('use_lockfile = true' in backend, f'{env} lockfile disabled')
    require('encrypt      = true' in backend, f'{env} encryption flag missing')
    require((root/'main.tf').exists(),f'{env} root missing')
role=(ROOT/'examples/terraform/oidc-deployment-role/main.tf').read_text()
require('sts:AssumeRoleWithWebIdentity' in role,'OIDC federation absent')
require('token.actions.githubusercontent.com:sub' in role,'OIDC subject not validated')
require('token.actions.githubusercontent.com:aud' in role,'OIDC audience not validated')
require('"s3:DeleteObject"' in role and '.tflock' in role,'Lock-object permission missing')
require('"${local.state_bucket_arn}/${var.state_key}"' in role,'State object not scoped')
workflows=ROOT/'examples/github/workflows'
for f in workflows.glob('*.yml'):
    d=yaml.safe_load(f.read_text())
    require('jobs' in d,f'jobs missing in {f.name}')
    # PyYAML's YAML 1.1 parsing treats `on` as boolean, so verify source directly.
    require('\non:' in f.read_text(),f'trigger missing in {f.name}')
pr=(workflows/'terraform-validate.yml').read_text()
require('id-token: write' not in pr.split('# Add an organization-controlled')[0], 'PR workflow requests OIDC')
require('pull_request_target' not in pr,'Unsafe PR trigger')
deploy=(workflows/'terraform-deploy.yml').read_text()
require("github.ref == 'refs/heads/main'" in deploy,'Main guard absent')
require('environment:' in deploy,'Protected environment absent')
require('get-caller-identity' in deploy,'Expected account check absent')
require('terraform plan' in deploy and 'terraform apply' in deploy,'Plan/apply not paired')
require('cancel-in-progress: false' in deploy,'Deploy concurrency not safe')
for n in range(1,7):
    require((ROOT/f'adrs/adr-{n:04d}.tex').exists(),f'Missing ADR-{n:04d}')
with (ROOT/'governance/control-matrix.csv').open() as f:
    rows=list(csv.DictReader(f))
require(len(rows)>=20,'Insufficient control evidence coverage')
if issues:
    print('FAIL:')
    for item in issues: print(' -',item)
    sys.exit(1)
print('PASS: package cross-references, control matrix, trust-model patterns, YAML and 6 ADRs')
