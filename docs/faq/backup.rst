Backup and restore
------------------

The service provides several commands aim to do easy repository backup and restore. If you would like to move repository from the server ``server1.example.com`` to another ``server2.example.com`` you have to perform the following steps:

#. 
   On the source server ``server1.example.com`` run ``repo-backup`` command, e.g.:

   .. code-block:: shell

      ahriman repo-backup /tmp/repo.tar.gz

   This command will pack all configuration files together with database file into the archive specified as command line argument (i.e. ``/tmp/repo.tar.gz``). In addition it will also archive ``cache`` directory (the one which contains local clones used by e.g. local packages) and ``.gnupg`` of the ``ahriman`` user.

#. 
   Copy created archive from source server ``server1.example.com`` to target ``server2.example.com``.

#. 
   Install package as usual on the target server ``server2.example.com`` if you didn't yet.

#. 
   Extract archive e.g. by using subcommand:

   .. code-block:: shell

      ahriman repo-restore /tmp/repo.tar.gz

   An additional argument ``-o``/``--output`` can be used to specify extraction root (``/`` by default).

#. 
   Rebuild repository:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-rebuild --from-database
