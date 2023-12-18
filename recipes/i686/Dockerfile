FROM arcan1s/ahriman:edge

ENV ARCH32_KEYRING_VERSION="20231126-1.0"

RUN pacman-key --init

RUN pacman -Sy --noconfirm wget && \
    wget -nv http://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-${ARCH32_KEYRING_VERSION}-any.pkg.tar.zst && \
    pacman -U --noconfirm archlinux32-keyring-${ARCH32_KEYRING_VERSION}-any.pkg.tar.zst
