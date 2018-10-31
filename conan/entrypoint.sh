#!/usr/bin/env sh
gunicorn \
    --bind=0.0.0.0:${CONAN_PORT} \
    --workers=${CONAN_WORKERS} \
    --timeout=${CONAN_TIMEOUT} \
    conans.server.server_launcher:app
