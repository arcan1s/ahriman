#!/bin/bash

set -e

VERSION="$1"
ARCHIVE="ahriman"
FILES="COPYING README.md package src setup.py"
IGNORELIST="build .idea package/archlinux package/*src.tar.xz"

# set version
sed -i "/__version__ = '[0-9.]*/s/[^'][^)]*/__version__ = '$VERSION'/" src/ahriman/version.py

# create archive
[[ -e ${ARCHIVE}-${VERSION}-src.tar.xz ]] && rm -f "${ARCHIVE}-${VERSION}-src.tar.xz"
[[ -d $ARCHIVE ]] && rm -rf "$ARCHIVE"
mkdir "$ARCHIVE"
for FILE in ${FILES[*]}; do cp -r "$FILE" "$ARCHIVE"; done
for FILE in ${IGNORELIST[*]}; do rm -rf "${ARCHIVE}/${FILE}"; done
tar cJf "${ARCHIVE}-${VERSION}-src.tar.xz" "$ARCHIVE"
rm -rf "$ARCHIVE"

# update checksums
SHA512SUMS=$(sha512sum ${ARCHIVE}-${VERSION}-src.tar.xz | awk '{print $1}')
sed -i "/sha512sums=('[0-9A-Fa-f]*/s/[^'][^)]*/sha512sums=('$SHA512SUMS'/" package/archlinux/PKGBUILD
sed -i "s/pkgver=[0-9.]*/pkgver=$VERSION/" package/archlinux/PKGBUILD

# clear
find . -type f -name '*src.tar.xz' -not -name "*${VERSION}-src.tar.xz" -exec rm -rf {} \;

exit 0

# tag
git add package/archlinux/PKGBUILD
git commit -m "Release $VERSION" && git push
git tag $VERSION && git push --tags
