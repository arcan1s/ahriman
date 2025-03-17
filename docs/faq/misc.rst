Other topics
------------

How does it differ from %another-manager%?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Short answer - I do not know. Also for some references credits to `Alad <https://github.com/AladW>`__, he `did <https://wiki.archlinux.org/title/User:Alad/Local_repo_tools>`__ really good investigation of existing alternatives.

`arch-repo-manager <https://github.com/Martchus/arch-repo-manager>`__
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Looks actually pretty good, in case if I would find it, I would probably didn't start this project; the most of features (like web interface or additional helpers) are already implemented or planned to be. However, this project seems to be at early alpha stage (as for Nov 2022), written in C++ (not pro or con) and misses documentation.

`archrepo2 <https://github.com/lilydjwg/archrepo2>`__
"""""""""""""""""""""""""""""""""""""""""""""""""""""

Don't know, haven't tried it. But it lacks of documentation at least.

* ``ahriman`` has web interface.
* ``archrepo2`` doesn't have synchronization and reporting.
* ``archrepo2`` actively uses direct shell calls and ``yaourt`` components.
* ``archrepo2`` has constantly running process instead of timer process (it is not pro or con).

`repoctl <https://github.com/cassava/repoctl>`__
""""""""""""""""""""""""""""""""""""""""""""""""

* ``ahriman`` has web interface.
* ``repoctl`` does not have reporting feature.
* ``repoctl`` does not support local packages and patches.
* Some actions are not fully automated in ``repoctl`` (e.g. package update still requires manual intervention for the build itself).
* ``repoctl`` has better AUR interaction features. With colors!
* ``repoctl`` has much easier configuration and even completion.
* ``repoctl`` is able to store old packages.
* Ability to host repository from same command in ``repoctl`` vs external services (e.g. nginx) in ``ahriman``.

`repod <https://gitlab.archlinux.org/archlinux/repod>`__
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Official tool provided by distribution, has clean logic, but it is just a helper for ``repo-add``, e.g. it doesn't work with AUR and all packages builds have to be handled separately.

`repo-scripts <https://github.com/arcan1s/repo-scripts>`__
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Though originally I've created ahriman by trying to improve the project, it still lacks a lot of features:

* ``ahriman`` has web interface.
* ``ahriman`` has better reporting with template support.
* ``ahriman`` has more synchronization features (there was only ``rsync`` based).
* ``ahriman`` supports local packages and patches.
* ``repo-scripts`` doesn't have dependency management.

...and so on. ``repo-scripts`` also has bad architecture and bad quality code and uses out-of-dated ``yaourt`` and ``package-query``.

`toolbox <https://github.com/chaotic-aur/toolbox>`__
""""""""""""""""""""""""""""""""""""""""""""""""""""

It is automation tools for ``repoctl`` mentioned above. Except for using shell it looks pretty cool and also offers some additional features like patches, remote synchronization (isn't it?) and reporting.

`AURCache <https://github.com/Lukas-Heiligenbrunner/AURCache>`__
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

That's really cool project if you are looking for simple service to build AUR packages. It provides very informative dashboard and easy to configure and use. However, it doesn't provide direct way to control build process (e.g. it is neither trivial to build packages for architectures which are not supported by default nor to change build flags).

Also this application relies on docker setup (e.g. builders are only available as special docker containers). In addition, it uses ``paru`` to build packages instead of ``devtools``.

How to check service logs
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the service writes logs to ``journald`` which can be accessed by using ``journalctl`` command (logs are written to the journal of the user under which command is run). In order to retrieve logs for the process you can use the following command:

.. code-block:: shell

   sudo journalctl SYSLOG_IDENTIFIER=ahriman

You can also ask to forward logs to ``stderr``, just set ``--log-handler`` flag, e.g.:

.. code-block:: shell

   ahriman --log-handler console ...

You can even configure logging as you wish, but kindly refer to python ``logging`` module `configuration <https://docs.python.org/3/library/logging.config.html>`__.

The application uses java concept to log messages, e.g. class ``Application`` imported from ``ahriman.application.application`` package will have logger called ``ahriman.application.application.Application``. In order to e.g. change logger name for whole application package it is possible to change values for ``ahriman.application`` package; thus editing ``ahriman`` logger configuration will change logging for whole application (unless there are overrides for another logger).

Html customization
^^^^^^^^^^^^^^^^^^

It is possible to customize html templates. In order to do so, create files somewhere (refer to Jinja2 documentation and the service source code for available parameters) and prepend ``templates`` with value pointing to this directory.

In addition, default html templates supports style customization out-of-box. In order to customize style, just put file named ``user-style.jinja2`` to the templates directory.

Web API extension
^^^^^^^^^^^^^^^^^

The application loads web views dynamically, so it is possible relatively easy extend its API. In order to do so:

#. Create view class which is derived from ``ahriman.web.views.base.BaseView`` class.
#. Create implementation for this class.
#. Put file into ``ahriman.web.views`` package.
#. Restart application.

For more details about implementation and possibilities, kindly refer to module documentation and source code and `aiohttp documentation <https://docs.aiohttp.org/en/stable/>`__.

I did not find my question
^^^^^^^^^^^^^^^^^^^^^^^^^^

`Create an issue <https://github.com/arcan1s/ahriman/issues>`__ with type **Question**.
