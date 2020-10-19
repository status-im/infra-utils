#!/usr/bin/env bash

OLD_TAG=${1}
NEW_TAG=${OLD_TAG%-mobile}

echo "OLD: ${OLD_TAG}"
echo "NEW: ${NEW_TAG}"

COMMIT=$(git rev-parse ${OLD_TAG})
echo "COMMIT: ${COMMIT}"

git tag --delete ${OLD_TAG}
git push origin --delete ${OLD_TAG}

git tag ${NEW_TAG} ${COMMIT}
git push origin --tags
