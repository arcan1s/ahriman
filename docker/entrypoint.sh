#!/bin/bash

set -e
[ -n "$AHRIMAN_DEBUG" ] && set -x

AHRIMAN_DEFAULT_ARGS=("--architecture" "$AHRIMAN_ARCHITECTURE")
AHRIMAN_DEFAULT_ARGS+=("--repository" "$AHRIMAN_REPOSITORY")
if [ -n "$AHRIMAN_OUTPUT" ]; then
    AHRIMAN_DEFAULT_ARGS+=("--log-handler" "$AHRIMAN_OUTPUT")
fi

# create .gnupg directory which is required for keys
AHRIMAN_GNUPG_HOME="$(getent passwd "$AHRIMAN_USER" | cut -d : -f 6)/.gnupg"
[ -d "$AHRIMAN_GNUPG_HOME" ] || mkdir -m700 "$AHRIMAN_GNUPG_HOME"

# run built-in setup command
AHRIMAN_SETUP_ARGS=("--build-as-user" "$AHRIMAN_USER")
AHRIMAN_SETUP_ARGS+=("--packager" "$AHRIMAN_PACKAGER")
if [ -z "$AHRIMAN_MULTILIB" ]; then
    AHRIMAN_SETUP_ARGS+=("--no-multilib")
fi
if [ -n "$AHRIMAN_PACMAN_MIRROR" ]; then
    AHRIMAN_SETUP_ARGS+=("--mirror" "$AHRIMAN_PACMAN_MIRROR")
fi
if [ -n "$AHRIMAN_REPOSITORY_SERVER" ]; then
    AHRIMAN_SETUP_ARGS+=("--server" "$AHRIMAN_REPOSITORY_SERVER")
fi
if [ -n "$AHRIMAN_PORT" ]; then
    AHRIMAN_SETUP_ARGS+=("--web-port" "$AHRIMAN_PORT")
fi
if [ -n "$AHRIMAN_UNIX_SOCKET" ]; then
    AHRIMAN_SETUP_ARGS+=("--web-unix-socket" "$AHRIMAN_UNIX_SOCKET")
fi

[ -n "$AHRIMAN_PRESETUP_COMMAND" ] && eval "$AHRIMAN_PRESETUP_COMMAND"
ahriman "${AHRIMAN_DEFAULT_ARGS[@]}" service-setup "${AHRIMAN_SETUP_ARGS[@]}"
[ -n "$AHRIMAN_POSTSETUP_COMMAND" ] && eval "$AHRIMAN_POSTSETUP_COMMAND"

# validate configuration if set
[ -n "$AHRIMAN_VALIDATE_CONFIGURATION" ] && ahriman "${AHRIMAN_DEFAULT_ARGS[@]}" service-config-validate --exit-code

# special workaround to emulate /bin/bash entrypoint if first argument starts with /
[[ "$1" =~ ^/.* ]] && exec "$@"

exec ahriman "${AHRIMAN_DEFAULT_ARGS[@]}" "$@"
