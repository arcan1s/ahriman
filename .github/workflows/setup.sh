#!/bin/bash
# Install the package and run main install commands

set -ex

# install dependencies
echo -e '[arcanisrepo]\nServer = http://repo.arcanis.me/$arch\nSigLevel = Never' | tee -a /etc/pacman.conf
# refresh the image
pacman --noconfirm -Syu
# main dependencies
pacman --noconfirm -Sy base-devel devtools git pyalpm python-aur python-passlib python-srcinfo sudo
# make dependencies
pacman --noconfirm -Sy python-pip
# optional dependencies
# VCS support
pacman --noconfirm -Sy breezy darcs mercurial subversion
# web server
pacman --noconfirm -Sy python-aioauth-client python-aiohttp python-aiohttp-debugtoolbar python-aiohttp-jinja2 python-aiohttp-security python-aiohttp-session python-cryptography python-jinja
# additional features
pacman --noconfirm -Sy gnupg python-boto3 rsync

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

# special thing for the container, because /dev/log interface is not available there
sed -i "s/handlers = syslog_handler/handlers = console_handler/g" /etc/ahriman.ini.d/logging.ini
# initial setup command as root
ahriman -a x86_64 repo-setup --packager "ahriman bot <ahriman@example.com>" --repository "github" --web-port 8080
# enable services
systemctl enable ahriman-web@x86_64
systemctl enable ahriman@x86_64.timer
# run web service (detached)
sudo -u ahriman -- ahriman -a x86_64 web &
WEBPID=$!
sleep 15s  # wait for the web service activation
# add the first package
# the build itself does not really work in the container
sudo -u ahriman -- ahriman package-add --now yay
# check if package was actually installed
#test -n "$(find "/var/lib/ahriman/repository/x86_64" -name "yay*pkg*")"
# run package check
sudo -u ahriman -- ahriman repo-update
# stop web service lol
kill $WEBPID
