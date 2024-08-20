Non-x86_64 architecture setup
-----------------------------

The following section describes how to setup ahriman with architecture different from x86_64, as example i686. For most cases you have base repository available, e.g. archlinux32 repositories for i686 architecture; in case if base repository is not available, steps are a bit different, however, idea remains the same.

The example of setup with docker compose can be found `here <https://github.com/arcan1s/ahriman/tree/master/recipes/i686>`__.

Physical server setup
^^^^^^^^^^^^^^^^^^^^^

In this example we are going to use files and packages which are provided by official repositories of the used architecture. Note, that versions might be different, thus you need to find correct versions on the distribution web site, e.g. `archlinux32 packages <https://www.archlinux32.org/packages/>`__.

#.
   First, considering having base Arch Linux system, we need to install keyring for the specified repositories, e.g.:

   .. code-block:: shell

      wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst
      pacman -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   In order to run ``devtools`` scripts for custom architecture they also need specific ``makepkg`` configuration, it can be retrieved by installing the ``devtools`` package of the distribution, e.g.:

   .. code-block:: shell

      wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst
      pacman -U devtools-20221208-1.2-any.pkg.tar.zst

   Alternatively, you can create your own ``makepkg`` configuration and save it as ``/usr/share/devtools/makepkg.conf.d/i686.conf``.

#.
   Setup repository as usual:

   .. code-block:: shell

      ahriman -a i686 service-setup --mirror 'https://de.mirror.archlinux32.org/$arch/$repo'--no-multilib ...

   In addition to usual options, you need to specify the following options:

   * ``--mirror`` - link to the mirrors which will be used instead of official repositories.
   * ``--no-multilib`` - in the example we are using i686 architecture for which multilib repository doesn't exist.

#.
   That's all Folks!

Docker container setup
^^^^^^^^^^^^^^^^^^^^^^

There are two possible ways to achieve same setup, by using docker container. The first one is just mount required files inside container and run it as usual (with specific environment variables). Another one is to create own container based on official one:

#.
   Clone official container as base:

   .. code-block:: dockerfile

      FROM arcan1s/ahriman:latest

#.
   Init pacman keys. This command is required in order to populate distribution keys:

   .. code-block:: dockerfile

      RUN pacman-key --init

#.
   Install packages as it was described above:

   .. code-block:: dockerfile

      RUN pacman --noconfirm -Sy wget
      RUN wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.2-any.pkg.tar.zst
      RUN wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   At that point you should have full ``Dockerfile`` like:

   .. code-block:: dockerfile

      FROM arcan1s/ahriman:latest

      RUN pacman-key --init

      RUN pacman --noconfirm -Sy wget
      RUN wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.2-any.pkg.tar.zst
      RUN wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   After that you can build you own container, e.g.:

   .. code-block:: shell

      docker build --tag ahriman-i686:latest

#.
   Now you can run locally built container as usual with passing environment variables for setup command:

   .. code-block:: shell

      docker run --privileged -p 8080:8080 -e AHRIMAN_ARCHITECTURE=i686 -e AHRIMAN_PACMAN_MIRROR='https://de.mirror.archlinux32.org/$arch/$repo' -e AHRIMAN_MULTILIB= ahriman-i686:latest
