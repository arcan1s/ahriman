Initial setup
=============

#. 
   Install package as usual.
#. 
   Change settings if required, see :doc:`configuration reference <configuration>` for more details.
#.
   TL;DR

   .. code-block:: shell

      sudo ahriman -a x86_64 repo-setup ...

   ``repo-setup`` literally does the following steps:

   #.
      Create ``/var/lib/ahriman/.makepkg.conf`` with ``makepkg.conf`` overrides if required (at least you might want to set ``PACKAGER``\ ):

      .. code-block:: shell

          echo 'PACKAGER="John Doe <john@doe.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf

   #.
      Configure build tools (it is required for correct dependency management system):

      #. 
         Create build command, e.g. ``ln -s /usr/bin/archbuild /usr/local/bin/ahriman-x86_64-build`` (you can choose any name for command, basically it should be ``{name}-{arch}-build``\ ).
      #. 
         Create configuration file, e.g. ``cp /usr/share/devtools/pacman-{extra,ahriman}.conf`` (same as previous ``pacman-{name}.conf``\ ).
      #. 
         Change configuration file, add your own repository, add multilib repository etc;
      #. 
         Set ``build_command`` option to point to your command.
      #.
         Configure ``/etc/sudoers.d/ahriman`` to allow running command without a password.

         .. code-block:: shell

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

#. 
   Start and enable ``ahriman@.timer`` via ``systemctl``\ :

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
