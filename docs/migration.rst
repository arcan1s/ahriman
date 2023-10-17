Manual migrations
=================

Normally most of migrations are handled automatically after application start. However, some upgrades require manual interventions; this document describes them.

Upgrades to breakpoints
-----------------------

To 2.9.0
^^^^^^^^

This release includes major upgrade for the newest devtools and archlinux repository structure. In order to upgrade package need to:

#. Upgrade to the latest major release of python (3.11) (required by other changes).
#. Upgrade devtools to the latest release.
#. Backup your settings, ``/etc/ahriman.ini.d/00-setup-overrides.ini`` by default.
#. Run setup command (i.e. ``ahriman service-setup``) again with the same arguments as you used before. This step can be done manually by moving ``devtools`` configuration (something like ``/usr/share/devtools/pacman-ahriman*.conf``) to new location ``/usr/share/devtools/pacman.conf.d/`` under name ``ahriman.conf``. After that make sure to remove any ``community`` mentions from configurations (e.g. ``/usr/share/devtools/pacman.conf.d/ahriman.conf``, ``/etc/ahriman.ini``) if there were any. The only thing which will change is ``devtools`` configuration.
#. Remove build chroot as it is incompatible, e.g. ``sudo ahriman service-clean --chroot``.
#. Run ``sudo -u ahriman ahriman update --no-aur --no-local --no-manual -yy`` in order to update local databases.

To 2.12.0
^^^^^^^^^

This release includes paths migration. Unlike usual case, no automatic migration is performed because it might break user configuration. The following noticeable changes have been made:

* Path to pre-built packages now includes repository name, i.e. it has been changed from ``/var/lib/ahriman/packages/x86_64`` to ``/var/lib/ahriman/packages/aur-clone/x86_64``.
* Path to pacman databases now includes repository name too, it has been changed from ``/var/lib/ahriman/pacman/x86_64`` to ``/var/lib/ahriman/pacman/aur-clone/x86_64``.
* Path to repository itself also includes repository name, from ``/var/lib/ahriman/repository/x86_64`` to ``/var/lib/ahriman/repository/aur-clone/x86_64``.

In order to migrate to new filesystem tree the following actions are required:

#.
   Stop and disable all services, e.g. timer and web service:

   .. code-block:: shell

      sudo systemctl disable --now ahriman@x86_64.timer
      sudo systemctl disable --now ahriman-web@x86_64

#.
   Create directory tree. It can be done by running ``ahriman service-tree-migrate`` subcommand. It performs copying between the old repository tree and the new one. Alternatively you can copy directories by hands.

#.
   Edit configuration in case if anything is pointing to the old path, e.g. HTML report generation, in the way in which it will be pointed to directory inside repository specific one, e.g. ``/var/lib/ahriman/repository/x86_64`` to ``/var/lib/ahriman/repository/aur-clone/x86_64``.

#.
   Edit devtools pacman configuration (``/usr/share/devtools/pacman.conf.d/ahriman-x86_64.conf`` by default) replacing ``Server`` with path to your repository, e.g.:

   .. code-block:: ini

      [aur-clone]
      SigLevel = Optional TrustAll
      Server = file:///var/lib/ahriman/repository/aur-clone/x86_64

   Alternatively it can be done by running ``service-setup`` command again.

#. If you didn't run setup command on the previous step, make sure to remove architecture reference from ``web`` section (if any).

#.
   Make sure to update remote synchronization services if any. Almost all of them rely on current repository tree by default, so you need to setup either redirects or configure to synchronize to the old locations (e.g. ``object_path`` option for S3 synchronization).

#.
   Enable and start services again. Unit template parameter should include both repository architecture and name, dash separated, e.g. ``x86_64-aur-clone``:

   .. code-block:: shell

      sudo systemctl enable --now ahriman@x86_64-aur-clone.timer
      sudo systemctl enable --now ahriman-web
