FROM archlinux:base

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
## refresh packages, install sudo and install packages for building
RUN pacman -Syu --noconfirm sudo && \
    pacman -S --noconfirm --asdeps fakeroot python-tox
## create build user
RUN useradd -m -d "/home/build" -s "/usr/bin/nologin" build && \
    echo "build ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/build"
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
        python-hatchling \
        python-installer \
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

## FIXME since 1.0.4 devtools requires dbus to be run, which doesn't work now in container
COPY "docker/systemd-nspawn.sh" "/usr/local/bin/systemd-nspawn"

# install ahriman
## copy tree
COPY --chown=build . "/home/build/ahriman"
## create package archive and install it
RUN cd "/home/build/ahriman" && \
    tox -e archive && \
    cp ./dist/*.tar.gz "package/archlinux" && \
    cd "package/archlinux" && \
    runuser -u build -- makepkg --noconfirm --install --skipchecksums && \
    cd / && rm -r "/home/build/ahriman"

# cleanup unused
RUN find "/var/cache/pacman/pkg" -type f -delete
RUN pacman -Qdtq | pacman -Rscn --noconfirm -

VOLUME ["/var/lib/ahriman"]

# minimal runtime ahriman setup
COPY "docker/entrypoint.sh" "/usr/local/bin/entrypoint"
ENTRYPOINT ["entrypoint"]
# default command
CMD ["repo-update", "--refresh"]
