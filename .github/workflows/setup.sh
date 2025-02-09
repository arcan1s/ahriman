#!/bin/bash
# Install the package and run main install commands

set -ex

[[ $1 = "minimal" ]] && MINIMAL_INSTALL=1

# install dependencies
echo -e '[arcanisrepo]\nServer = https://repo.arcanis.me/$arch\nSigLevel = Never' | tee -a /etc/pacman.conf
# refresh the image
pacman -Syyu --noconfirm
# main dependencies
pacman -S --noconfirm devtools git pyalpm python-bcrypt python-inflection python-pyelftools python-requests python-systemd sudo
# make dependencies
pacman -S --noconfirm --asdeps base-devel python-build python-flit python-installer python-tox python-wheel
# optional dependencies
if [[ -z $MINIMAL_INSTALL ]]; then
    # web server
    pacman -S --noconfirm python-aioauth-client python-aiohttp python-aiohttp-apispec-git python-aiohttp-cors python-aiohttp-jinja2 python-aiohttp-security python-aiohttp-session python-cryptography python-jinja
    # additional features
    pacman -S --noconfirm gnupg ipython python-boto3 python-cerberus python-matplotlib rsync
fi
# FIXME since 1.0.4 devtools requires dbus to be run, which doesn't work now in container
cp "docker/systemd-nspawn.sh" "/usr/local/bin/systemd-nspawn"

# create fresh tarball
tox -e archive
# run makepkg
PKGVER=$(python -c "from src.ahriman import __version__; print(__version__)")
mv "dist/ahriman-$PKGVER.tar.gz" package/archlinux
chmod +777 package/archlinux  # because fuck you that's why
cd package/archlinux
sudo -u nobody -- makepkg -cf --skipchecksums --noconfirm
sudo -u nobody -- makepkg --packagelist | grep "ahriman-core-$PKGVER" | pacman -U --noconfirm --nodeps -
if [[ -z $MINIMAL_INSTALL ]]; then
    sudo -u nobody -- makepkg --packagelist | grep "ahriman-triggers-$PKGVER" | pacman -U --noconfirm --nodeps -
    sudo -u nobody -- makepkg --packagelist | grep "ahriman-web-$PKGVER" | pacman -U --noconfirm --nodeps -
fi
# create machine-id which is required by build tools
systemd-machine-id-setup

# remove unused dependencies
pacman -Qdtq | pacman -Rscn --noconfirm -

# initial setup command as root
[[ -z $MINIMAL_INSTALL ]] && WEB_ARGS=("--web-port" "8080")
ahriman -a x86_64 -r "github" service-setup --packager "ahriman bot <ahriman@example.com>" "${WEB_ARGS[@]}"
# enable services
systemctl enable ahriman@x86_64-github.timer
if [[ -z $MINIMAL_INSTALL ]]; then
    # validate configuration
    ahriman service-config-validate --exit-code
    # run web service (detached)
    systemctl enable ahriman-web
    sudo -u ahriman -- ahriman web &
    WEB_PID=$!
fi
# add the first package
sudo -u ahriman -- ahriman --log-handler console package-add --now ahriman
# check if package was actually installed
test -n "$(find "/var/lib/ahriman/repository/github/x86_64" -name "ahriman*pkg*")"
# run package check
sudo -u ahriman -- ahriman repo-update
# stop web service lol
[[ -z $WEB_PID ]] || kill $WEB_PID
