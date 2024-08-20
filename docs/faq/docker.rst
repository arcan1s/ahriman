Docker image
------------

We provide official images which can be found under:

* docker registry ``arcan1s/ahriman``;
* ghcr.io registry ``ghcr.io/arcan1s/ahriman``.

These images are totally identical.

Docker image is being updated on each commit to master as well as on each version. If you would like to use last (probably unstable) build you can use ``edge`` tag or ``latest`` for any tagged versions; otherwise you can use any version tag available.

The default action (in case if no arguments provided) is ``repo-update``. Basically the idea is to run container, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

``--privileged`` flag is required to make mount possible inside container. In order to make data available outside of container, you would need to mount local (parent) directory inside container by using ``-v /path/to/local/repo:/var/lib/ahriman`` argument, where ``/path/to/local/repo`` is a path to repository on local machine. In addition, you can pass own configuration overrides by using the same ``-v`` flag, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman -v /path/to/overrides/overrides.ini:/etc/ahriman.ini.d/10-overrides.ini arcan1s/ahriman:latest

The action can be specified during run, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest package-add ahriman --now

For more details please refer to the docker FAQ.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The following environment variables are supported:

* ``AHRIMAN_ARCHITECTURE`` - architecture of the repository, default is ``x86_64``.
* ``AHRIMAN_DEBUG`` - if set all commands will be logged to console.
* ``AHRIMAN_FORCE_ROOT`` - force run ahriman as root instead of guessing by subcommand.
* ``AHRIMAN_HOST`` - host for the web interface, default is ``0.0.0.0``.
* ``AHRIMAN_MULTILIB`` - if set (default) multilib repository will be used, disabled otherwise.
* ``AHRIMAN_OUTPUT`` - controls logging handler, e.g. ``syslog``, ``console``. The name must be found in logging configuration. Note that if ``syslog`` handler is used you will need to mount ``/dev/log`` inside container because it is not available there.
* ``AHRIMAN_PACKAGER`` - packager name from which packages will be built, default is ``ahriman bot <ahriman@example.com>``.
* ``AHRIMAN_PACMAN_MIRROR`` - override pacman mirror server if set.
* ``AHRIMAN_PORT`` - HTTP server port if any, default is empty.
* ``AHRIMAN_POSTSETUP_COMMAND`` - if set, the command which will be called (as root) after the setup command, but before any other actions.
* ``AHRIMAN_PRESETUP_COMMAND`` - if set, the command which will be called (as root) right before the setup command.
* ``AHRIMAN_REPOSITORY`` - repository name, default is ``aur-clone``.
* ``AHRIMAN_REPOSITORY_SERVER`` - optional override for the repository URL. Useful if you would like to download packages from remote instead of local filesystem.
* ``AHRIMAN_REPOSITORY_ROOT`` - repository root. Because of filesystem rights it is required to override default repository root. By default, it uses ``ahriman`` directory inside ahriman's home, which can be passed as mount volume.
* ``AHRIMAN_UNIX_SOCKET`` - full path to unix socket which is used by web server, default is empty. Note that more likely you would like to put it inside ``AHRIMAN_REPOSITORY_ROOT`` directory (e.g. ``/var/lib/ahriman/ahriman/ahriman-web.sock``) or to ``/run/ahriman``.
* ``AHRIMAN_USER`` - ahriman user, usually must not be overwritten, default is ``ahriman``.
* ``AHRIMAN_VALIDATE_CONFIGURATION`` - if set (default) validate service configuration.

You can pass any of these variables by using ``-e`` argument, e.g.:

.. code-block:: shell

   docker run --privileged -e AHRIMAN_PORT=8080 -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Daemon service
^^^^^^^^^^^^^^

There is special ``repo-daemon`` subcommand which emulates systemd timer and will perform repository update periodically:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest repo-daemon

This command uses same rules as ``repo-update``, thus, e.g. requires ``--privileged`` flag. Check also `examples <https://github.com/arcan1s/ahriman/tree/master/recipes/daemon>`__.

Web service setup
^^^^^^^^^^^^^^^^^

For that you would need to have web container instance running forever; it can be achieved by the following command:

.. code-block:: shell

   docker run --privileged -p 8080:8080 -e AHRIMAN_PORT=8080 -e AHRIMAN_UNIX_SOCKET=/var/lib/ahriman/ahriman/ahriman-web.sock -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Note about ``AHRIMAN_PORT`` environment variable which is required in order to enable web service. An additional port bind by ``-p 8080:8080`` is required to pass docker port outside of container.

The ``AHRIMAN_UNIX_SOCKET`` variable is not required, however, highly recommended as it can be used for interprocess communications. If you set this variable you would like to be sure that this path is available outside of container if you are going to use multiple docker instances.

If you are using ``AHRIMAN_UNIX_SOCKET`` variable, for every next container run it has to be passed also, e.g.:

.. code-block:: shell

   docker run --privileged -e AHRIMAN_UNIX_SOCKET=/var/lib/ahriman/ahriman/ahriman-web.sock -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Otherwise, you would need to pass ``AHRIMAN_PORT`` and mount container network to the host system (``--net=host``), e.g.:

.. code-block:: shell

   docker run --privileged --net=host -e AHRIMAN_PORT=8080 -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Simple server with authentication can be found in `examples <https://github.com/arcan1s/ahriman/tree/master/recipes/web>`__ too.

Mutli-repository web service
""""""""""""""""""""""""""""

Idea is pretty same as to just run web service. However, it is required to run setup commands for each repository, except for one which is specified by ``AHRIMAN_REPOSITORY`` and ``AHRIMAN_ARCHITECTURE`` variables.

In order to create configuration for additional repositories, the ``AHRIMAN_POSTSETUP_COMMAND`` variable should be used, e.g.:

.. code-block:: shell

   docker run --privileged -p 8080:8080 -e AHRIMAN_PORT=8080 -e AHRIMAN_UNIX_SOCKET=/var/lib/ahriman/ahriman/ahriman-web.sock -e AHRIMAN_POSTSETUP_COMMAND="ahriman --architecture x86_64 --repository aur-clone-v2 service-setup --build-as-user ahriman --packager 'ahriman bot <ahriman@example.com>'" -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

The command above will also create configuration for the repository named ``aur-clone-v2``.

Note, however, that the command above is only required in case if the service is going to be used to run subprocesses. Otherwise, everything else (web interface, status, etc) will be handled as usual.

Configuration `example <https://github.com/arcan1s/ahriman/tree/master/recipes/multirepo>`__.
