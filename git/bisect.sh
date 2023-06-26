#!/usr/bin/env bash

GOOD="${1}"
BAD="${2}"
COMMAND="${3}"
REPEAT="${3:-1}"

[[ -z "${GOOD}" ]]    && { echo "No bisect good commit provided!" >&2; exit 1; }
[[ -z "${BAD}" ]]     && { echo "No bisect bad commit provided!"  >&2; exit 1; }
[[ -z "${COMMAND}" ]] && { echo "No bisect command provided!"     >&2; exit 1; }

git bisect start
git bisect good "${GOOD}"
git bisect bad  "${BAD}"
git bisect run bash -c "${COMMAND}"
git bisect log
git bisect visualize --stat
git bisect reset
