#!/usr/bin/env bash
ROLES_DIR="${HOME}/.ansible/roles"
mkdir -p "${ROLES_DIR}"

for DIR in ${HOME}/work/infra-role-*; do
    REPO_NAME=$(basename "${DIR}")
    echo "Symlinking: ${REPO_NAME}"
    ln -fs "${DIR}" "${ROLES_DIR}"
    # Symlink also without 'infra-role-' prefix
    ln -fs "${DIR}" "${ROLES_DIR}/${REPO_NAME#infra-role-}"
done
