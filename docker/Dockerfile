# build image
FROM archlinux:base AS build

# install environment
## create build user
RUN useradd -m -d "/home/build" -s "/usr/bin/nologin" build

## extract container creation date and set mirror for this timestamp, set PKGEXT and refresh database next
RUN echo "Server = https://archive.archlinux.org/repos/$(stat -c "%y" "/var/lib/pacman" | cut -d " " -f 1 | sed "s,-,/,g")/\$repo/os/\$arch" > "/etc/pacman.d/mirrorlist" && \
    pacman -Sy
## setup package cache
RUN runuser -u build -- mkdir "/tmp/pkg" && \
    echo "PKGDEST=/tmp/pkg" >> "/etc/makepkg.conf" && \
    echo "[options]" >> "/etc/pacman.conf" && \
    echo "CacheDir = /tmp/pkg/" >> "/etc/pacman.conf"

## install anc configure sudo
RUN pacman -S --noconfirm --asdeps sudo && \
    echo "build ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/build"
## copy install script
COPY "docker/install-aur-package.sh" "/usr/local/bin/install-aur-package"
## install package dependencies
RUN pacman -S --noconfirm --asdeps \
        devtools \
        git \
        pyalpm \
        python-bcrypt  \
        python-inflection \
        python-pyelftools \
        python-requests \
        && \
    pacman -S --noconfirm --asdeps \
        base-devel \
        python-build \
        python-flit \
        python-installer \
        python-tox \
        python-wheel \
        && \
    pacman -S --noconfirm --asdeps \
        git \
        python-aiohttp \
        python-boto3 \
        python-cerberus \
        python-cryptography \
        python-jinja \
        python-systemd \
        rsync \
        && \
    runuser -u build -- install-aur-package \
        python-aioauth-client \
        python-sphinx-typlog-theme \
        python-webargs \
        python-aiohttp-apispec-git \
        python-aiohttp-cors \
        python-aiohttp-jinja2 \
        python-aiohttp-session \
        python-aiohttp-security \
        python-requests-unixsocket2

# install ahriman
## copy tree
COPY --chown=build . "/home/build/ahriman"
## create package archive and install it
RUN cd "/home/build/ahriman" && \
    tox -e archive && \
    cp ./dist/*.tar.gz "package/archlinux" && \
    cd "package/archlinux" && \
    runuser -u build -- makepkg --noconfirm --skipchecksums && \
    cd / && rm -r "/home/build/ahriman"


# main image
FROM archlinux:base AS ahriman

# image configuration
ENV AHRIMAN_ARCHITECTURE="x86_64"
ENV AHRIMAN_DEBUG=""
ENV AHRIMAN_FORCE_ROOT=""
ENV AHRIMAN_HOST="0.0.0.0"
ENV AHRIMAN_MULTILIB="yes"
ENV AHRIMAN_OUTPUT=""
ENV AHRIMAN_PACKAGER="ahriman bot <ahriman@example.com>"
ENV AHRIMAN_PACMAN_MIRROR=""
ENV AHRIMAN_PORT=""
ENV AHRIMAN_POSTSETUP_COMMAND=""
ENV AHRIMAN_PRESETUP_COMMAND=""
ENV AHRIMAN_REPOSITORY="aur"
ENV AHRIMAN_REPOSITORY_SERVER=""
ENV AHRIMAN_REPOSITORY_ROOT="/var/lib/ahriman/ahriman"
ENV AHRIMAN_UNIX_SOCKET=""
ENV AHRIMAN_USER="ahriman"
ENV AHRIMAN_VALIDATE_CONFIGURATION="yes"

# install environment
## update pacman.conf with multilib
RUN echo "[multilib]" >> "/etc/pacman.conf" && \
    echo "Include = /etc/pacman.d/mirrorlist" >> "/etc/pacman.conf"
## copy built packages from build image and setup repository
COPY --from=build "/tmp/pkg" "/var/cache/pacman/pkg"
RUN repo-add "/var/cache/pacman/pkg/core.db.tar.zst" "/var/cache/pacman/pkg/"*.pkg.tar.zst && \
    repo-add "/var/cache/pacman/pkg/extra.db.tar.zst" && \
    repo-add "/var/cache/pacman/pkg/multilib.db.tar.zst"
## set local directory to use as repository and refresh database
RUN cp "/etc/pacman.d/mirrorlist" "/etc/pacman.d/mirrorlist.orig" && \
    echo "Server = file:///var/cache/pacman/pkg" > "/etc/pacman.d/mirrorlist" && \
    cp "/etc/pacman.conf" "/etc/pacman.conf.orig" && \
    sed -i "s/SigLevel *=.*/SigLevel = Optional/g" "/etc/pacman.conf" && \
    pacman -Sy
## install package and its optional dependencies
RUN pacman -S --noconfirm ahriman
RUN pacman -S --noconfirm --asdeps \
        python-aioauth-client \
        python-aiohttp-apispec-git \
        python-aiohttp-security \
        python-aiohttp-session \
        python-boto3 \
        python-cerberus \
        python-cryptography \
        python-systemd \
        python-requests-unixsocket2 \
        rsync \
        sudo

## clear cache and restore system
RUN find "/var/cache/pacman/pkg" "/var/lib/pacman/sync" -type "f,l" -delete && \
    cp "/etc/pacman.d/mirrorlist.orig" "/etc/pacman.d/mirrorlist" && \
    cp "/etc/pacman.conf.orig" "/etc/pacman.conf"

VOLUME ["/var/lib/ahriman"]

# minimal runtime ahriman setup
## FIXME since 1.0.4 devtools requires dbus to be run, which doesn't work now in container
COPY "docker/systemd-nspawn.sh" "/usr/local/bin/systemd-nspawn"
## entrypoint setup
COPY "docker/entrypoint.sh" "/usr/local/bin/entrypoint"
COPY "docker/entrypoint-web.sh" "/usr/local/bin/entrypoint-web"
ENTRYPOINT ["entrypoint"]
# default command
CMD ["repo-update", "--refresh"]
