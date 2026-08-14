#!/bin/bash
# Special workaround for running web service in github actions, must not be usually used in real environment,
# consider running web command explicitly instead

if (( EUID == 0 )); then
    chown ahriman:ahriman /var/lib/ahriman
    exec sudo -E -u ahriman -- entrypoint web "$@"
fi

exec entrypoint web "$@"
