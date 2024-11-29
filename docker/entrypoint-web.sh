#!/bin/bash
# Special workaround for running web service in github actions, must not be usually used in real environment,
# consider running web command explicitly instead

exec entrypoint web "$@"