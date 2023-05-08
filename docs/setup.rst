Initial setup
=============

#. 
   Install package as usual.
#. 
   Change settings if required, see :doc:`configuration reference <configuration>` for more details.
#.
   Perform initial setup:

   .. code-block:: shell

      sudo ahriman -a x86_64 service-setup ...

   ``service-setup`` literally does the following steps:

   #.
      Create ``/var/lib/ahriman/.makepkg.conf`` with ``makepkg.conf`` overrides if required (at least you might want to set ``PACKAGER``):

      .. code-block:: shell

          echo 'PACKAGER="John Doe <john@doe.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf

   #.
      Configure build tools (it is required for correct dependency management system):

      #.
         Create configuration file ``{repository}.conf``:

         .. code-block:: shell

            cp /usr/local/share/devtools-git-poc/pacman.conf.d/{extra,aur-clone}.conf

      #. 
         Change configuration file, add your own repository, add multilib repository etc:

         .. code-block:: shell

            echo '[multilib]' | tee -a /usr/local/share/devtools-git-poc/pacman.conf.d/aur-clone.conf
            echo 'Include = /etc/pacman.d/mirrorlist' | tee -a /usr/local/share/devtools-git-poc/pacman.conf.d/aur-clone.conf

            echo '[aur-clone]' | tee -a /usr/local/share/devtools-git-poc/pacman.conf.d/aur-clone.conf
            echo 'SigLevel = Optional TrustAll' | tee -a /usr/local/share/devtools-git-poc/pacman.conf.d/aur-clone.conf
            echo 'Server = file:///var/lib/ahriman/repository/$arch' | tee -a /usr/local/share/devtools-git-poc/pacman.conf.d/aur-clone.conf

      #.
         Configure ``/etc/sudoers.d/ahriman`` to allow running devtools command without a password:

         .. code-block:: shell

            echo 'Cmnd_Alias CARCHBUILD_CMD = /usr/bin/pkgctl build *' | tee -a /etc/sudoers.d/ahriman
            echo 'ahriman ALL=(ALL) NOPASSWD: CARCHBUILD_CMD' | tee -a /etc/sudoers.d/ahriman
            chmod 400 /etc/sudoers.d/ahriman

      This command supports several arguments, kindly refer to its help message.

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

       sudo -u ahriman ahriman -a x86_64 package-add ahriman --now --refresh

   The ``--refresh`` flag is required in order to handle local database update.
