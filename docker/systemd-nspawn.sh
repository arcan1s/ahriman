#!/bin/bash
# Since https://gitlab.archlinux.org/archlinux/devtools/-/commit/5f4fd52e3836ddddb25a0f9e15d0acfed06f693d
# it is impossible to start devtools inside docker container, because it requires slice registering
# which is impossible because there is no init in container

is_slice() {
    [[ $1 =~ ^--slice* ]]
}

allowed=()
for arg in "$@"; do
    is_slice "$arg" && allowed+=("--keep-unit") || allowed+=("$arg")
done

exec /usr/bin/systemd-nspawn "${allowed[@]}"
