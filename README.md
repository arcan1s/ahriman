# ArcHlinux ReposItory MANager

Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Installation and run

* Install package as usual.
* Change settings if required, see `CONFIGURING.md` for more details.
* Create `/var/lib/ahriman/.makepkg.conf` with `makepkg.conf` overrides if required (at least you might want to set `PACKAGER`).
* Configure build tools (it might be required if your package will use any custom repositories):
    * create build command if required, e.g. `ln -s /usr/bin/archbuild /usr/local/bin/custom-x86_64-build` (you can choose any name for command);
    * create configuration file, e.g. `cp /usr/share/devtools/pacman-{extra,custom}.conf`;
    * change configuration file: add your own repository, add multilib repository;
    * set `build.build_command` to point to your command;
    * configure `/etc/sudoers.d/ahriman` to allow to run command without password.
* Start and enable `ahriman.timer` via `systemctl`.
* Add packages by using `ahriman add {package}` command.

## Limitations

* It does not manage dependencies, so you have to add them before main package.