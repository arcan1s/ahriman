# ArcHlinux ReposItory MANager

[![build status](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml)

Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Features

* Install-configure-forget manager for own repository
* Multi-architecture support
* VCS packages support
* Sign support with gpg (repository, package, per package settings)
* Synchronization to remote services (rsync, s3) and report generation (html)
* Dependency manager
* Repository status interface

## Installation and run

* Install package as usual.
* Change settings if required, see [CONFIGURING](CONFIGURING.md) for more details.
* Create `/var/lib/ahriman/.makepkg.conf` with `makepkg.conf` overrides if required (at least you might want to set `PACKAGER`):

    ```shell
    echo 'PACKAGER="John Doe <john@doe.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf
    ```

* Configure build tools (it is required for correct dependency management system):

    * create build command, e.g. `ln -s /usr/bin/archbuild /usr/local/bin/ahriman-x86_64-build` (you can choose any name for command, basically it should be `{name}-{arch}-build`);
    * create configuration file, e.g. `cp /usr/share/devtools/pacman-{extra,ahriman}.conf` (same as previous `pacman-{name}.conf`);
    * change configuration file, add your own repository, add multilib repository etc;
    * set `build_command` option to point to your command;
    * configure `/etc/sudoers.d/ahriman` to allow running command without a password.

    ```shell
    ln -s /usr/bin/archbuild /usr/local/bin/ahriman-x86_64-build
    cp /usr/share/devtools/pacman-{extra,ahriman}.conf

    echo '[multilib]' | tee -a /usr/share/devtools/pacman-ahriman.conf
    echo 'Include = /etc/pacman.d/mirrorlist' | tee -a /usr/share/devtools/pacman-ahriman.conf

    echo '[aur-clone]' | tee -a /usr/share/devtools/pacman-ahriman.conf
    echo 'SigLevel = Optional TrustAll' | tee -a /usr/share/devtools/pacman-ahriman.conf
    echo 'Server = file:///var/lib/ahriman/repository/$arch' | tee -a /usr/share/devtools/pacman-ahriman.conf

    echo '[build]' | tee -a /etc/ahriman.ini.d/build.ini
    echo 'build_command = ahriman-x86_64-build' | tee -a /etc/ahriman.ini.d/build.ini

    echo 'Cmnd_Alias CARCHBUILD_CMD = /usr/local/bin/ahriman-x86_64-build *' | tee -a /etc/sudoers.d/ahriman
    echo 'ahriman ALL=(ALL) NOPASSWD: CARCHBUILD_CMD' | tee -a /etc/sudoers.d/ahriman
    chmod 400 /etc/sudoers.d/ahriman
    ```

* Start and enable `ahriman@.timer` via `systemctl`:

    ```shell
    systemctl enable --now ahriman@x86_64.timer
    ```

* Start and enable status page:

    ```shell
    systemctl enable --now ahriman-web@x86_64
    ```

* Add packages by using `ahriman add {package}` command:

    ```shell
    sudo -u ahriman ahriman -a x86_64 add yay --now
    ```

Note that initial service configuration can be done by running `ahriman setup` with specific arguments.
