Distributed builds
------------------

The service allows to run build on multiple machines and collect packages on main node. There are several ways to achieve it, this section describes officially supported methods.

Remote synchronization and remote server call
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This setup requires at least two instances of the service:

#. Web service (with opt-in authorization enabled), later will be referenced as ``master`` node.
#. Application instances responsible for build, later will be referenced as ``worker`` nodes.

In this example the following settings are assumed:

* Repository architecture is ``x86_64``.
* Master node address is ``master.example.com``.

Master node configuration
"""""""""""""""""""""""""

The only requirements for the master node is that API must be available for worker nodes to call (e.g. port must be exposed to internet, or local network in case of VPN, etc) and file upload must be enabled:

.. code-block:: ini

   [web]
   enable_archive_upload = yes

In addition, the following settings are recommended for the master node:

*
  As it has been mentioned above, it is recommended to enable authentication (see :doc:`How to enable basic authorization <web>`) and create system user which will be used later. Later this user (if any) will be referenced as ``worker-user``.

*
  In order to be able to spawn multiple processes at the same time, wait timeout must be configured:

  .. code-block:: ini

     [web]
     wait_timeout = 0

Worker nodes configuration
""""""""""""""""""""""""""

#.
   First of all, in this setup you need to split your repository into chunks manually, e.g. if you have repository on master node with packages ``A``, ``B`` and ``C``, you need to split them between all available workers, as example:

   * Worker #1: ``A``.
   * Worker #2: ``B`` and ``C``.

   Hint: ``repo-tree`` subcommand provides ``--partitions`` argument.

#.
   Each worker must be configured to upload files to master node:

   .. code-block:: ini

      [upload]
      target = remote-service

      [remote-service]

#.
   Worker must be configured to access web on master node:

   .. code-block:: ini

      [status]
      address = https://master.example.com
      username = worker-user
      password = very-secure-password

   As it has been mentioned above, ``status.address`` must be available for workers. In case if unix socket is used, it can be passed in the same option as usual. Optional ``status.username``/``status.password`` can be supplied in case if authentication was enabled on master node.

#.
   Each worker must call master node on success:

   .. code-block:: ini

      [report]
      target = remote-call

      [remote-call]
      manual = yes

   After success synchronization (see above), the built packages will be put into directory, from which they will be read during manual update, thus ``remote-call.manual`` flag is required.

#.
   Change order of trigger runs. This step is required, because by default the report trigger is called before the upload trigger and we would like to achieve the opposite:

   .. code-block:: ini

      [build]
      triggers = ahriman.core.gitremote.RemotePullTrigger ahriman.core.upload.UploadTrigger ahriman.core.report.ReportTrigger ahriman.core.gitremote.RemotePushTrigger

In addition, the following settings are recommended for workers:

*
  You might want to wait until report trigger will be completed; in this case the following option must be set:

  .. code-block:: ini

     [remote-call]
     wait_timeout = 0

Dependency management
"""""""""""""""""""""

By default worker nodes don't know anything about master nodes packages, thus it will try to build each dependency by its own. However, using ``AHRIMAN_REPOSITORY_SERVER`` docker variable (or ``--server`` flag for setup command), it is possible to specify address of the master node for devtools configuration.

Repository and packages signing
"""""""""""""""""""""""""""""""

You can sign packages on worker nodes and then signatures will be synced to master node. In order to do so, you need to configure worker node as following, e.g.:

.. code-block:: ini

   [sign]
   target = package
   key = 8BE91E5A773FB48AC05CC1EDBED105AED6246B39

Note, however, that in this case, signatures will not be validated on master node and just will be copied to repository tree.

If you would like to sign only database files (aka repository sign), it has to be configured only on master node as usual, e.g.:

.. code-block:: ini

   [sign]
   target = repository
   key = 8BE91E5A773FB48AC05CC1EDBED105AED6246B39

Double node minimal docker example
""""""""""""""""""""""""""""""""""

Master node config (``master.ini``) as:

.. code-block:: ini

   [auth]
   target = configuration

   [web]
   enable_archive_upload = yes
   wait_timeout = 0


Command to run master node:

.. code-block:: shell

   docker run --privileged -p 8080:8080 -e AHRIMAN_PORT=8080 -v master.ini:/etc/ahriman.ini.d/overrides.ini arcan1s/ahriman:latest web

The user ``worker-user`` has been created additionally. Worker node config (``worker.ini``) as:

.. code-block:: ini

   [status]
   address = http://172.17.0.1:8080
   username = worker-user
   password = very-secure-password

   [upload]
   target = remote-service

   [remote-service]

   [report]
   target = remote-call

   [remote-call]
   manual = yes
   wait_timeout = 0

   [build]
   triggers = ahriman.core.gitremote.RemotePullTrigger ahriman.core.upload.UploadTrigger ahriman.core.report.ReportTrigger ahriman.core.gitremote.RemotePushTrigger

The address above (``http://172.17.0.1:8080``) is somewhat available for worker container.

Command to run worker node:

.. code-block:: shell

   docker run --privileged -v worker.ini:/etc/ahriman.ini.d/overrides.ini -it arcan1s/ahriman:latest package-add ahriman --now

The command above will successfully build ``ahriman`` package, upload it on master node and, finally, will update master node repository.

Check proof-of-concept setup `here <https://github.com/arcan1s/ahriman/tree/master/recipes/distributed-manual>`__.

Addition of new package and repository update
"""""""""""""""""""""""""""""""""""""""""""""

Just run on worker command as usual, the built packages will be automatically uploaded to master node. Note that automatic update process must be disabled on master node.

Package removal
"""""""""""""""

This action must be done in two steps:

#. Remove package on worker.
#. Remove package on master node.

Delegate builds to remote workers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This setup heavily uses upload feature described above and, in addition, also delegates build process automatically to build machines. Same as above, there must be at least two instances available (``master`` and ``worker``), however, all ``worker`` nodes must be run in the web service mode.

Master node configuration
"""""""""""""""""""""""""

In addition to the configuration above, the worker list must be defined in configuration file (``build.workers`` option), i.e.:

.. code-block:: ini

   [build]
   workers = https://worker1.example.com https://worker2.example.com

   [web]
   enable_archive_upload = yes
   wait_timeout = 0

In the example above, ``https://worker1.example.com`` and ``https://worker2.example.com`` are remote ``worker`` node addresses available for ``master`` node.

In case if authentication is required (which is recommended way to setup it), it can be set by using ``status`` section as usual.

Worker nodes configuration
""""""""""""""""""""""""""

It is required to point to the master node repository, otherwise internal dependencies will not be handled correctly. In order to do so, the ``--server`` argument (or ``AHRIMAN_REPOSITORY_SERVER`` environment variable for docker images) can be used.

Also, in case if authentication is enabled, the same user with the same password must be created for all workers.

It is also recommended to set ``web.wait_timeout`` to infinite in case of multiple conflicting runs and ``service_only`` to ``yes`` in order to disable status endpoints.

Other settings are the same as mentioned above.

Triple node minimal docker example
""""""""""""""""""""""""""""""""""

In this example, all instances are run on the same machine with address ``172.17.0.1`` with ports available outside of container. Master node config (``master.ini``) as:

.. code-block:: ini

   [auth]
   target = configuration

   [status]
   username = builder-user
   password = very-secure-password

   [build]
   workers = http://172.17.0.1:8081 http://172.17.0.1:8082

   [web]
   enable_archive_upload = yes
   wait_timeout = 0

Command to run master node:

.. code-block:: shell

   docker run --privileged -p 8080:8080 -e AHRIMAN_PORT=8080 -v master.ini:/etc/ahriman.ini.d/overrides.ini arcan1s/ahriman:latest web

Worker nodes (applicable for all workers) config (``worker.ini``) as:

.. code-block:: ini

   [auth]
   target = configuration

   [status]
   address = http://172.17.0.1:8080
   username = builder-user
   password = very-secure-password

   [upload]
   target = remote-service

   [remote-service]

   [report]
   target = remote-call

   [remote-call]
   manual = yes
   wait_timeout = 0

   [web]
   service_only = yes

   [build]
   triggers = ahriman.core.upload.UploadTrigger ahriman.core.report.ReportTrigger

Command to run worker nodes (considering there will be two workers, one is on ``8081`` port and other is on ``8082``):

.. code-block:: shell

   docker run --privileged -p 8081:8081 -e AHRIMAN_PORT=8081 -v worker.ini:/etc/ahriman.ini.d/overrides.ini arcan1s/ahriman:latest web
   docker run --privileged -p 8082:8082 -e AHRIMAN_PORT=8082 -v worker.ini:/etc/ahriman.ini.d/overrides.ini arcan1s/ahriman:latest web

Unlike the previous setup, it doesn't require to mount repository root for ``worker`` nodes, because they don't use it anyway.

Check proof-of-concept setup `here <https://github.com/arcan1s/ahriman/tree/master/recipes/distributed>`__.

Addition of new package, package removal, repository update
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

In all scenarios, update process must be run only on ``master`` node. Unlike the manually distributed packages described above, automatic update must be enabled only for ``master`` node.

Automatic worker nodes discovery
""""""""""""""""""""""""""""""""

Instead of setting ``build.workers`` option it is also possible to configure services to load worker list dynamically. To do so, the ``ahriman.core.distributed.WorkerLoaderTrigger`` and ``ahriman.core.distributed.WorkerTrigger`` must be used for ``master`` and ``worker`` nodes repsectively. See recipes for more details.

Known limitations
"""""""""""""""""

* Workers don't support local packages. However, it is possible to build custom packages by providing sources by using ``ahriman.core.gitremote.RemotePullTrigger`` trigger.
* No dynamic nodes discovery. In case if one of worker nodes is unavailable, the build process will fail.
* No pkgrel bump on conflicts.
* The identical user must be created for all workers. However, the ``master`` node user can be different from this one.
