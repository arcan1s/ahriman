Initial setup
=============

#. 
   Install package(s) as usual. At least, ``ahriman-core`` package is required; other features can be installed separately. Alternatively, it is possible to install meta-package, which includes everything.
#. 
   Change settings if required, see :doc:`configuration reference <configuration>` for more details.
#.
   Perform initial setup:

   .. code-block:: shell

      sudo ahriman -a x86_64 -r aur service-setup ...

   .. admonition:: Details
      :collapsible: closed

      ``service-setup`` literally does the following steps:

      #.
         Create ``/var/lib/ahriman/.makepkg.conf`` with ``makepkg.conf`` overrides if required (at least you might want to set ``PACKAGER``):

         .. code-block:: shell

            echo 'PACKAGER="ahriman bot <ahriman@example.com>"' | sudo -u ahriman tee -a /var/lib/ahriman/.makepkg.conf

      #.
         Configure build tools (it is required for correct dependency management system):

          #.
             Create configuration file ``{name}.conf`` or ``{name}-{arch}.conf``, where ``name`` is the repostory name and ``arch`` is the repository architecture, e.g.:

             .. code-block:: shell

                cp /usr/share/devtools/pacman.conf.d/{extra,aur-x86_64}.conf

          #.
             Change configuration file, add your own repository, add multilib repository etc:

             .. code-block:: shell

                echo '[multilib]' | tee -a /usr/share/devtools/pacman.conf.d/aur-x86_64.conf
                echo 'Include = /etc/pacman.d/mirrorlist' | tee -a /usr/share/devtools/pacman.conf.d/aur-x86_64.conf

                echo '[aur]' | tee -a /usr/share/devtools/pacman.conf.d/aur-x86_64.conf
                echo 'SigLevel = Optional TrustAll' | tee -a /usr/share/devtools/pacman.conf.d/aur-x86_64.conf
                echo 'Server = file:///var/lib/ahriman/repository/$repo/$arch' | tee -a /usr/share/devtools/pacman.conf.d/aur-x86_64.conf

   This command supports several arguments, kindly refer to its help message.

#. 
   Start and enable ``ahriman@.timer`` via ``systemctl``:

   .. code-block:: shell

       systemctl enable --now ahriman@x86_64-aur.timer

#. 
   Start and enable status page:

   .. code-block:: shell

       systemctl enable --now ahriman-web

#. 
   Add packages by using ``ahriman package-add {package}`` command:

   .. code-block:: shell

       sudo -u ahriman ahriman package-add ahriman --now --refresh

   The ``--refresh`` flag is required in order to handle local database update.
