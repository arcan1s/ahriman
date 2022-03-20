FROM archlinux:base-devel

# image configuration
ENV AHRIMAN_ARCHITECTURE="x86_64"
ENV AHRIMAN_DEBUG=""
ENV AHRIMAN_FORCE_ROOT=""
ENV AHRIMAN_OUTPUT="syslog"
ENV AHRIMAN_PACKAGER="ahriman bot <ahriman@example.com>"
ENV AHRIMAN_PORT=""
ENV AHRIMAN_REPOSITORY="aur-clone"
ENV AHRIMAN_REPOSITORY_ROOT="/var/lib/ahriman/ahriman"
ENV AHRIMAN_USER="ahriman"

# install environment
## install git which is required for AUR interaction and go for yay
RUN pacman --noconfirm -Syu git go
## create build user
RUN useradd -m -d /home/build -s /usr/bin/nologin build && \
    echo "build ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/build
## install AUR helper
RUN YAY_DIR="$(runuser -u build -- mktemp -d)" && \
    git clone https://aur.archlinux.org/yay.git "$YAY_DIR" && \
    cd "$YAY_DIR" && \
    runuser -u build -- makepkg --noconfirm --install && \
    cd - && rm -r "$YAY_DIR"
## install package dependencies
RUN runuser -u build -- yay --noconfirm -Sy devtools git pyalpm python-inflection python-passlib python-requests python-srcinfo && \
    runuser -u build -- yay --noconfirm -Sy python-build python-installer python-wheel && \
    runuser -u build -- yay --noconfirm -Sy breezy darcs mercurial python-aioauth-client python-aiohttp \
                                            python-aiohttp-debugtoolbar python-aiohttp-jinja2 python-aiohttp-security \
                                            python-aiohttp-session python-boto3 python-cryptography python-jinja \
                                            rsync subversion

# install ahriman
## copy tree
COPY --chown=build . "/home/build/ahriman"
## create package archive and install it
RUN cd "/home/build/ahriman" && \
    make VERSION=$(python -c "from src.ahriman.version import __version__; print(__version__)") archlinux && \
    cp ./*-src.tar.xz "package/archlinux" && \
    cd "package/archlinux" && \
    runuser -u build -- makepkg --noconfirm --install --skipchecksums && \
    cd - && rm -r "/home/build/ahriman"

VOLUME ["/var/lib/ahriman"]

# minimal runtime ahriman setup
COPY "docker/entrypoint.sh" "/usr/local/bin/entrypoint"
ENTRYPOINT ["entrypoint"]
# default command
CMD ["repo-update"]
