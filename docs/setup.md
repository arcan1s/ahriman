# Setup instructions

1. Install package as usual.
2. Change settings if required, see [configuration reference](configuration.md) for more details.
3. TL;DR

   ```shell
   sudo ahriman -a x86_64 repo-setup ...
   ```
   
   `repo-setup` literally does the following steps:

   1. Create `/var/lib/ahriman/.makepkg.conf` with `makepkg.conf` overrides if required (at least you might want to set `PACKAGER`):

       ```shell
       echo 'PACKAGER="John Doe <john@doe.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf
       ```

   2. Configure build tools (it is required for correct dependency management system):

       1. Create build command, e.g. `ln -s /usr/bin/archbuild /usr/local/bin/ahriman-x86_64-build` (you can choose any name for command, basically it should be `{name}-{arch}-build`).
       2. Create configuration file, e.g. `cp /usr/share/devtools/pacman-{extra,ahriman}.conf` (same as previous `pacman-{name}.conf`).
       3. Change configuration file, add your own repository, add multilib repository etc;
       4. Set `build_command` option to point to your command.
       5. Configure `/etc/sudoers.d/ahriman` to allow running command without a password.

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

4. Start and enable `ahriman@.timer` via `systemctl`:

    ```shell
    systemctl enable --now ahriman@x86_64.timer
    ```

5. Start and enable status page:

    ```shell
    systemctl enable --now ahriman-web@x86_64
    ```

6. Add packages by using `ahriman package-add {package}` command:

    ```shell
    sudo -u ahriman ahriman -a x86_64 package-add ahriman --now
    ```

## User creation

`user-add` subcommand is recommended for new user creation.