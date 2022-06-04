Initial setup
=============

#. 
   Install package as usual.
#. 
   Change settings if required, see :doc:`configuration reference <configuration>` for more details.
#.
   TL;DR:

   .. code-block:: shell

      sudo ahriman -a x86_64 repo-setup ...

   ``repo-setup`` literally does the following steps:

   #.
      Create ``/var/lib/ahriman/.makepkg.conf`` with ``makepkg.conf`` overrides if required (at least you might want to set ``PACKAGER``):

      .. code-block:: shell

          echo 'PACKAGER="John Doe <john@doe.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf

   #.
      Configure build tools (it is required for correct dependency management system):

      #. 
         Create build command (you can choose any name for command, basically it should be ``{name}-{arch}-build``):

         .. code-block:: shell

            ln -s /usr/bin/archbuild /usr/local/bin/ahriman-x86_64-build

      #. 
         Create configuration file (same as previous ``pacman-{name}.conf``):

         .. code-block:: shell

            cp /usr/share/devtools/pacman-{extra,ahriman}.conf

      #. 
         Change configuration file, add your own repository, add multilib repository etc:

         .. code-block:: shell

            echo '[multilib]' | tee -a /usr/share/devtools/pacman-ahriman.conf
            echo 'Include = /etc/pacman.d/mirrorlist' | tee -a /usr/share/devtools/pacman-ahriman.conf

            echo '[aur-clone]' | tee -a /usr/share/devtools/pacman-ahriman.conf
            echo 'SigLevel = Optional TrustAll' | tee -a /usr/share/devtools/pacman-ahriman.conf
            echo 'Server = file:///var/lib/ahriman/repository/$arch' | tee -a /usr/share/devtools/pacman-ahriman.conf

      #. 
         Set ``build_command`` option to point to your command:

         .. code-block:: shell

            echo '[build]' | tee -a /etc/ahriman.ini.d/build.ini
            echo 'build_command = ahriman-x86_64-build' | tee -a /etc/ahriman.ini.d/build.ini

      #.
         Configure ``/etc/sudoers.d/ahriman`` to allow running command without a password:

         .. code-block:: shell

            echo 'Cmnd_Alias CARCHBUILD_CMD = /usr/local/bin/ahriman-x86_64-build *' | tee -a /etc/sudoers.d/ahriman
            echo 'ahriman ALL=(ALL) NOPASSWD: CARCHBUILD_CMD' | tee -a /etc/sudoers.d/ahriman
            chmod 400 /etc/sudoers.d/ahriman

#. 
   Start and enable ``ahriman@.timer`` via ``systemctl``:

   .. code-block:: shell

       systemctl enable --now ahriman@x86_64.timer

#. 
   Start and enable status page:

   .. code-block:: shell

       systemctl enable --now ahriman-web@x86_64

#. 
   Add packages by using ``ahriman package-add {package}`` command:

   .. code-block:: shell

       sudo -u ahriman ahriman -a x86_64 package-add ahriman --now
