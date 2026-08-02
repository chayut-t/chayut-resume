#!/bin/sh
# Scan all tracked files for private info before committing.
# The patterns themselves are private, so they live in .pii-patterns,
# which is gitignored and never leaves this machine.
set -eu
cd "$(dirname "$0")/.."

if [ ! -f .pii-patterns ]; then
    echo "ERROR: .pii-patterns not found." >&2
    echo "Create it locally with one regex per line for each piece of private" >&2
    echo "info that must never be committed (phone, personal email, location)." >&2
    exit 2
fi

if git grep -nEi -f .pii-patterns -- $(git ls-files); then
    echo "PII FOUND in tracked files — do not commit/push." >&2
    exit 1
fi
echo "PII scan clean."
