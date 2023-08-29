#!/bin/bash
# Install the package and run main install commands

set -ex

[[ $1 = "minimal" ]] && MINIMAL_INSTALL=1

# install dependencies
echo -e '[arcanisrepo]\nServer = http://repo.arcanis.me/$arch\nSigLevel = Never' | tee -a /etc/pacman.conf
# refresh the image
pacman --noconfirm -Syu
# main dependencies
pacman --noconfirm -Sy base-devel devtools git pyalpm python-cerberus python-inflection python-passlib python-requests python-srcinfo python-systemd sudo
# make dependencies
pacman --noconfirm -Sy python-build python-flit python-installer python-wheel
# optional dependencies
if [[ -z $MINIMAL_INSTALL ]]; then
    # VCS support
    pacman --noconfirm -Sy breezy darcs mercurial subversion
    # web server
    pacman --noconfirm -Sy python-aioauth-client python-aiohttp python-aiohttp-apispec-git python-aiohttp-cors python-aiohttp-debugtoolbar python-aiohttp-jinja2 python-aiohttp-security python-aiohttp-session python-cryptography python-jinja
    # additional features
    pacman --noconfirm -Sy gnupg python-boto3 rsync
fi

# create fresh tarball
make VERSION=1.0.0 archlinux  # well, it does not really matter which version we will put here
# run makepkg
mv ahriman-*-src.tar.xz package/archlinux
chmod +777 package/archlinux  # because fuck you that's why
cd package/archlinux
sudo -u nobody -- makepkg -cf --skipchecksums --noconfirm
pacman --noconfirm -U ahriman-1.0.0-1-any.pkg.tar.zst
# create machine-id which is required by build tools
systemd-machine-id-setup

# initial setup command as root
[[ -z $MINIMAL_INSTALL ]] && WEB_ARGS=("--web-port" "8080")
ahriman -a x86_64 -r "github" service-setup --packager "ahriman bot <ahriman@example.com>" "${WEB_ARGS[@]}"
# validate configuration
ahriman -a x86_64 -r "github" service-config-validate --exit-code
# enable services
systemctl enable ahriman-web@x86_64
systemctl enable ahriman@x86_64.timer
if [[ -z $MINIMAL_INSTALL ]]; then
    # run web service (detached)
    sudo -u ahriman -- ahriman -a x86_64 web &
    WEB_PID=$!
fi
# add the first package
sudo -u ahriman -- ahriman package-add --now ahriman
# check if package was actually installed
test -n "$(find "/var/lib/ahriman/repository/github/x86_64" -name "ahriman*pkg*")"
# run package check
sudo -u ahriman -- ahriman repo-update
# stop web service lol
[[ -z $WEB_PID ]] || kill $WEB_PID
