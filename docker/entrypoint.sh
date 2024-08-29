#!/bin/bash

set -e
[ -n "$AHRIMAN_DEBUG" ] && set -x

# configuration tune
cat <<EOF > "/etc/ahriman.ini.d/00-docker.ini"
[repository]
root = $AHRIMAN_REPOSITORY_ROOT

[web]
host = $AHRIMAN_HOST

EOF

AHRIMAN_DEFAULT_ARGS=("--architecture" "$AHRIMAN_ARCHITECTURE")
AHRIMAN_DEFAULT_ARGS+=("--repository" "$AHRIMAN_REPOSITORY")
if [ -n "$AHRIMAN_OUTPUT" ]; then
    AHRIMAN_DEFAULT_ARGS+=("--log-handler" "$AHRIMAN_OUTPUT")
fi

# create repository root inside the [[mounted]] directory and set correct ownership
[ -d "$AHRIMAN_REPOSITORY_ROOT" ] || mkdir "$AHRIMAN_REPOSITORY_ROOT"
chown "$AHRIMAN_USER":"$AHRIMAN_USER" "$AHRIMAN_REPOSITORY_ROOT"

# create .gnupg directory which is required for keys
AHRIMAN_GNUPG_HOME="$(getent passwd "$AHRIMAN_USER" | cut -d : -f 6)/.gnupg"
[ -d "$AHRIMAN_GNUPG_HOME" ] || mkdir -m700 "$AHRIMAN_GNUPG_HOME"
chown "$AHRIMAN_USER":"$AHRIMAN_USER" "$AHRIMAN_GNUPG_HOME"

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

# create machine-id which is required by build tools
systemd-machine-id-setup &> /dev/null

# if AHRIMAN_FORCE_ROOT is set or command is unsafe we can run without sudo
# otherwise we prepend executable by sudo command
if [ -n "$AHRIMAN_FORCE_ROOT" ]; then
    AHRIMAN_EXECUTABLE=("ahriman")
elif ahriman help-commands-unsafe -- "$@" &> /dev/null; then
    AHRIMAN_EXECUTABLE=("sudo" "-E" "-u" "$AHRIMAN_USER" "--" "ahriman")
else
    AHRIMAN_EXECUTABLE=("ahriman")
fi
exec "${AHRIMAN_EXECUTABLE[@]}" "${AHRIMAN_DEFAULT_ARGS[@]}" "$@"
