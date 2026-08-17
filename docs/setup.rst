Initial setup
=============

#. 
   Install package(s) as usual. At least, ``ahriman-core`` package is required; other features can be installed separately. Alternatively, it is possible to install meta-package, which includes everything.
#. 
   Change settings if required, see :doc:`configuration reference <configuration>` for more details.
#.
   Perform initial setup:

   .. code-block:: shell

      sudo -u ahriman -- ahriman -a x86_64 -r aur service-setup \
          --packager "ahriman bot <ahriman@example.com>" ...

   .. admonition:: Details
      :collapsible: closed

      ``service-setup`` does the following steps:

      #.
         Create a repository-specific ahriman configuration below
         ``/var/lib/ahriman/.config/ahriman/ahriman.ini.d``. This configuration stores the
         packager identity, ``MAKEFLAGS`` and other options supplied on the command line.

      #.
         Generate the devtools pacman configuration in
         ``/var/lib/ahriman/.config/ahriman/pacman.conf.d``. The file is based on the
         configuration selected by ``--from-configuration`` and contains the requested mirror,
         multilib settings and the ahriman repository path.

      #.
         Create the repository directories, initialize the package repository and synchronize
         its pacman database.

      Both configuration locations are below the repository root and must be writable by the
      user running ahriman. Existing system-wide overrides remain supported; see
      :doc:`the 2.22.0 migration guide <migrations/2.22.0>` when upgrading.

   This command supports several arguments, kindly refer to its help message.

#. 
   Start and enable ``ahriman@.timer`` via ``systemctl``:

   .. code-block:: shell

       sudo systemctl enable --now ahriman@x86_64-aur.timer

#. 
   Start and enable status page:

   .. code-block:: shell

       sudo systemctl enable --now ahriman-web

#. 
   Add packages by using ``ahriman package-add {package}`` command:

   .. code-block:: shell

       sudo -u ahriman ahriman package-add ahriman --now --refresh

   The ``--refresh`` flag is required in order to handle local database update.
