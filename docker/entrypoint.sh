#!/bin/bash

set -e
[ -n "$AHRIMAN_DEBUG" ] && set -x

# configuration tune
cat <<EOF > "/etc/ahriman.ini.d/00-docker.ini"
[repository]
root = $AHRIMAN_REPOSITORY_ROOT

[settings]
database = $AHRIMAN_REPOSITORY_ROOT/ahriman.db

[web]
host = $AHRIMAN_HOST

EOF
sed -i "s|handlers = syslog_handler|handlers = ${AHRIMAN_OUTPUT}_handler|g" "/etc/ahriman.ini.d/logging.ini"

AHRIMAN_DEFAULT_ARGS=("--architecture" "$AHRIMAN_ARCHITECTURE")
if [[ "$AHRIMAN_OUTPUT" == "syslog" ]]; then
    if [ ! -e "/dev/log" ]; then
        # by default ahriman uses syslog which is not available inside container
        # to make noise less we force quiet mode in case if /dev/log was not mounted
        AHRIMAN_DEFAULT_ARGS+=("--quiet")
    fi
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
AHRIMAN_SETUP_ARGS+=("--repository" "$AHRIMAN_REPOSITORY")
if [ -n "$AHRIMAN_PORT" ]; then
    AHRIMAN_SETUP_ARGS+=("--web-port" "$AHRIMAN_PORT")
fi
if [ -n "$AHRIMAN_UNIX_SOCKET" ]; then
    AHRIMAN_SETUP_ARGS+=("--web-unix-socket" "$AHRIMAN_UNIX_SOCKET")
fi
ahriman "${AHRIMAN_DEFAULT_ARGS[@]}" service-setup "${AHRIMAN_SETUP_ARGS[@]}"

# validate configuration if set
[ -n "$AHRIMAN_VALIDATE_CONFIGURATION" ] && ahriman "${AHRIMAN_DEFAULT_ARGS[@]}" service-config-validate --exit-code

# create machine-id which is required by build tools
systemd-machine-id-setup &> /dev/null

# if AHRIMAN_FORCE_ROOT is set or command is unsafe we can run without sudo
# otherwise we prepend executable by sudo command
if [ -n "$AHRIMAN_FORCE_ROOT" ]; then
    AHRIMAN_EXECUTABLE=("ahriman")
elif ahriman help-commands-unsafe --command="$*" &> /dev/null; then
    AHRIMAN_EXECUTABLE=("sudo" "-u" "$AHRIMAN_USER" "--" "ahriman")
else
    AHRIMAN_EXECUTABLE=("ahriman")
fi
exec "${AHRIMAN_EXECUTABLE[@]}" "${AHRIMAN_DEFAULT_ARGS[@]}" "$@"
