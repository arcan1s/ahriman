#!/bin/bash

set -e

for PACKAGE in "$@"; do
    BUILD_DIR="$(mktemp -d)"
    # clone the remote source
    git clone https://aur.archlinux.org/"$PACKAGE".git "$BUILD_DIR"
    cd "$BUILD_DIR"
    # checkout to the image date
    git checkout "$(git rev-list -1 --before="$(stat -c "%y" "/var/lib/pacman" | cut -d " " -f 1)" master)"
    # build and install the package
    makepkg --nocheck --noconfirm --install --rmdeps --syncdeps
    cd /
    rm -r "$BUILD_DIR"
done
