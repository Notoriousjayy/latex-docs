#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 2 ]]; then echo 'usage: worktree.sh task-name destination' >&2; exit 2; fi
[[ "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]] || exit 2
git worktree add -b "task-$1" -- "$2" HEAD
