#!/bin/bash

set -e

for PACKAGE in "$@"; do
    BUILD_DIR="$(mktemp -d)"
    git clone https://aur.archlinux.org/"$PACKAGE".git "$BUILD_DIR"
    cd "$BUILD_DIR"
    makepkg --noconfirm --install --rmdeps --syncdeps
    cd /
    rm -r "$BUILD_DIR"
done
