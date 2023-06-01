#!/bin/bash
# Install the package and run main install commands

set -ex

[[ $1 = "minimal" ]] && MINIMAL_INSTALL=1

# install dependencies
echo -e '[arcanisrepo]\nServer = https://repo.arcanis.me/$arch\nSigLevel = Never' | tee -a /etc/pacman.conf
# refresh the image
pacman -Syu --noconfirm
# main dependencies
pacman -Sy --noconfirm devtools git pyalpm python-cerberus python-inflection python-passlib python-pyelftools python-requests python-srcinfo python-systemd sudo
# make dependencies
pacman -Sy --noconfirm python-build python-flit python-installer python-tox python-wheel
# optional dependencies
if [[ -z $MINIMAL_INSTALL ]]; then
    # VCS support
    pacman -Sy --noconfirm breezy darcs mercurial subversion
    # web server
    pacman -Sy --noconfirm python-aioauth-client python-aiohttp python-aiohttp-apispec-git python-aiohttp-cors python-aiohttp-jinja2 python-aiohttp-security python-aiohttp-session python-cryptography python-jinja
    # additional features
    pacman -Sy --noconfirm gnupg python-boto3 rsync
fi
# FIXME since 1.0.4 devtools requires dbus to be run, which doesn't work now in container
cp "docker/systemd-nspawn.sh" "/usr/local/bin/systemd-nspawn"

# create fresh tarball
tox -e archive
# run makepkg
mv dist/ahriman-*.tar.gz package/archlinux
chmod +777 package/archlinux  # because fuck you that's why
cd package/archlinux
sudo -u nobody -- makepkg -cf --skipchecksums --noconfirm
sudo -u nobody -- makepkg --packagelist | grep -v -- -debug- | pacman -U --noconfirm -
# create machine-id which is required by build tools
systemd-machine-id-setup

# initial setup command as root
[[ -z $MINIMAL_INSTALL ]] && WEB_ARGS=("--web-port" "8080")
ahriman -a x86_64 -r "github" service-setup --packager "ahriman bot <ahriman@example.com>" "${WEB_ARGS[@]}"
# validate configuration
ahriman service-config-validate --exit-code
# enable services
systemctl enable ahriman-web
systemctl enable ahriman@x86_64-github.timer
if [[ -z $MINIMAL_INSTALL ]]; then
    # run web service (detached)
    sudo -u ahriman -- ahriman web &
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
