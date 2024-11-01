Maintenance packages
--------------------

Those features require extensions package to be installed before, e.g.:

.. code-block:: shell

   yay -S ahriman-triggers

Generate keyring package
^^^^^^^^^^^^^^^^^^^^^^^^

The application provides special plugin which generates keyring package. This plugin heavily depends on ``sign`` group settings, however it is possible to override them. The minimal package can be generated in the following way:

#.
   Edit configuration:

   .. code-block:: ini

      [keyring]
      target = keyring-generator

   By default it will use ``${sign:key}`` as trusted key and all other keys as packagers ones. For all available options refer to :doc:`configuration </configuration>`.

#.
   Create package source files:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-create-keyring

   This command will generate PKGBUILD, revoked and trusted listings and keyring itself and will register the package in database.

#.
   Build new package as usual:

   .. code-block:: shell

      sudo -u ahriman ahriman package-add aur-keyring --source local --now

   where ``aur`` is your repository name.

This plugin might have some issues, in case of any of them, kindly create `new issue <https://github.com/arcan1s/ahriman/issues/new/choose>`__.

Generate mirrorlist package
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application provides special plugin which generates mirrorlist package also. It is possible to distribute this package as usual later. The package can be generated in the following way:

#.
   Edit configuration:

   .. code-block:: ini

      [mirrorlist]
      target = mirrorlist-generator

      [mirrorlist-generator]
      servers = https://repo.example.com/$arch

   The ``${mirrorlist-generator:servers}`` must contain list of available mirrors, the ``$arch`` and ``$repo`` variables are supported. For more options kindly refer to :doc:`configuration </configuration>`.

#.
   Create package source files:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-create-mirrorlist

   This command will generate PKGBUILD and mirrorlist file and will register the package in database.

#.
   Build new package as usual:

   .. code-block:: shell

      sudo -u ahriman ahriman package-add aur-mirrorlist --source local --now

   where ``aur`` is your repository name.
