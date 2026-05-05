#!/bin/bash

set -e

for PACKAGE in "$@"; do
    BUILD_DIR="$(mktemp -d)"
    # clone the remote source
    git clone https://aur.archlinux.org/"$PACKAGE".git "$BUILD_DIR"
    cd "$BUILD_DIR"
    # FIXME monkey patch PKGBUILD for python
    sed -i 's/python -m build/python -m build --skip-dependency-check/g' "PKGBUILD"
    # checkout to the image date
    git checkout "$(git rev-list -1 --before="$BUILD_DATE" master)"
    # build and install the package
    makepkg --nocheck --noconfirm --install --rmdeps --syncdeps
    cd /
    rm -r "$BUILD_DIR"
done
