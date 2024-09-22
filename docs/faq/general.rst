General topics
--------------

What is the purpose of the project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project has been created in order to maintain self-hosted Arch Linux user repository without manual intervention - checking for updates and building packages.

How to install ahriman
^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   yay -S ahriman
   ahriman -a x86_64 -r aur-clone service-setup --packager "ahriman bot <ahriman@example.com>"
   systemctl enable --now ahriman@x86_64-aur-clone.timer

Long answer
"""""""""""

The idea is to install the package as usual, create working directory tree, create configuration for ``sudo`` and ``devtools``. Detailed description of the setup instruction can be found :doc:`here </setup>`.

Run as daemon
"""""""""""""

The alternative way (though not recommended) is to run service instead of timer:

.. code-block:: shell

   systemctl enable --now ahriman-daemon@x86_64-aur-clone

How to validate settings
^^^^^^^^^^^^^^^^^^^^^^^^

There is special command which can be used in order to validate current configuration:

.. code-block:: shell

   ahriman service-config-validate --exit-code

This command will print found errors, based on `cerberus <https://docs.python-cerberus.org/>`__, e.g.:

.. code-block:: shell

   auth
                   ssalt: unknown field
                   target: none or more than one rule validate
                           oneof definition 0: unallowed value mapping
                           oneof definition 1: field 'salt' is required
                           oneof definition 2: unallowed value mapping
                           oneof definition 2: field 'salt' is required
                           oneof definition 2: field 'client_id' is required
                           oneof definition 2: field 'client_secret' is required
   gitremote
                   pull_url: unknown field

If an additional flag ``--exit-code`` is supplied, the application will return non-zero exit code, which can be used partially in scripts.

What does "architecture specific" mean / How to configure for different architectures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some sections can be configured per architecture. The service will merge architecture specific values into common settings. In order to specify settings for specific architecture you must point it in section name.

For example, the section

.. code-block:: ini

   [build]
   build_command = extra-x86_64-build

states that default build command is ``extra-x86_64-build``. But if there is section

.. code-block:: ini

   [build:i686]
   build_command = extra-i686-build

the ``extra-i686-build`` command will be used for ``i686`` architecture. You can also override settings for different repositories and architectures; in this case section names will be ``build:aur-clone`` (repository name only) and ``build:aur-clone:i686`` (both repository name and architecture).

How to generate build reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Normally you would probably like to generate only one report for the specific type, e.g. only one email report. In order to do so you will need to have the following configuration:

.. code-block:: ini

   [report]
   target = email

   [email]
   ...

or in case of multiple architectures and *different* reporting settings:

.. code-block:: ini

   [report]
   target = email

   [email:i686]
   ...

   [email:x86_64]
   ...

But for some cases you would like to have multiple different reports with the same type (e.g. sending different templates to different addresses). For these cases you will need to specify section name in target and type in section, e.g. the following configuration can be used:

.. code-block:: ini

   [report]
   target = email_1 email_2

   [email_1]
   type = email
   ...

   [email_2]
   type = email
   ...

How to add new package
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman --now

``--now`` flag is totally optional and just run ``repo-update`` subcommand after the registering the new package. Thus the extended flow is the following:

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman
   sudo -u ahriman ahriman repo-update

How to build package from local PKGBUILD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman package-add /path/to/local/directory/with/PKGBUILD --now

Before using this command you will need to create local directory and put ``PKGBUILD`` there. These packages will be stored locally and *will be ignored* during automatic update; in order to update the package you will need to run ``package-add`` command again.

How to copy package from another repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As simple as add package from archive. Considering case when you would like to copy package ``package`` with version ``ver-rel`` from repository ``source-repository`` to ``target-respository`` (same architecture), the command will be following:

.. code-block:: shell

   sudo -u ahriman ahriman -r target-repository package-add /var/lib/ahriman/repository/source-repository/x86_64/package-ver-rel-x86_64.pkg.tar.zst

In addition, you can remove source package as usual later.

This feature in particular useful if for managing multiple repositories like ``[testing]`` and ``[extra]``.

How to fetch PKGBUILDs from remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you could use ``RemotePullTrigger`` trigger. To do so you will need to configure trigger as following:

.. code-block:: ini

   [remote-pull]
   target = gitremote

   [gitremote]
   pull_url = https://github.com/username/repository

During the next application run it will fetch repository from the specified URL and will try to find packages there which can be used as local sources.

This feature can be also used to build packages which are not listed in AUR, the example of the feature use can be found `here <https://github.com/arcan1s/ahriman/tree/master/recipes/pull>`__.

How to push updated PKGBUILDs to remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you'd need to use another trigger called ``RemotePushTrigger``. Configure trigger as following:

.. code-block:: ini

   [remote-push]
   target = gitremote

   [gitremote]
   push_url = https://github.com/username/repository

Unlike ``RemotePullTrigger`` trigger, the ``RemotePushTrigger`` more likely will require authorization. It is highly recommended to use application tokens for that instead of using your password (e.g. for GitHub you can generate tokens `here <https://github.com/settings/tokens>`__ with scope ``public_repo``). Authorization can be supplied by using authorization part of the URL, e.g. ``https://key:token@github.com/username/repository``.

How to change PKGBUILDs before build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well it is supported also. The recommended way is to patch specific function, e.g. by running

.. code-block:: shell

   sudo -u ahriman ahriman patch-add ahriman version

This command will prompt for new value of the PKGBUILD variable ``version``. You can also write it to file and read from it:

.. code-block:: shell

   sudo -u ahriman ahriman patch-add ahriman version version.patch

The command also supports arrays, but in this case you need to specify full array, e.g.

.. code-block:: shell

   sudo -u ahriman ahriman patch-add ahriman depends

   Post new function or variable value below. Press Ctrl-D to finish:
   (python python-aiohttp)
   ^D

will set depends PKGBUILD variable (exactly) to array ``["python", "python-aiohttp"]``.

Alternatively you can create full-diff patches, which are calculated by using ``git diff`` from current PKGBUILD master branch:

#.
   Clone sources from AUR.

#.
   Make changes you would like to (e.g. edit ``PKGBUILD``, add external patches).

#.
   Run command

   .. code-block:: shell

      sudo -u ahriman ahriman patch-set-add /path/to/local/directory/with/PKGBUILD

The last command will calculate diff from current tree to the ``HEAD`` and will store it locally. Patches will be applied on any package actions (e.g. it can be used for dependency management).

It is also possible to create simple patch during package addition, e.g.:

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman --variable PKGEXT=.pkg.tar.xz

The ``--variable`` argument accepts variables in shell like format: quotation and lists are supported as usual, but functions are not. This feature is useful in particular in order to override specific makepkg variables during build.

How to build package from official repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is the same as adding any other package, but due to restrictions you must specify source explicitly, e.g.:

.. code-block:: shell

   sudo -u ahriman ahriman package-add pacman --source repository

This feature is heavily depends on local pacman cache. In order to use this feature it is recommended to either run ``pacman -Sy`` before the interaction or use internal application cache with ``--refresh`` flag.

Package build fails because it cannot validate PGP signature of source files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman service-key-import ...

How to update VCS packages
^^^^^^^^^^^^^^^^^^^^^^^^^^

Normally the service handles VCS packages correctly. The version is updated in clean chroot, no additional actions are required.

How to review changes before build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this scenario, the update process must be separated into several stages. First, it is required to check updates:

.. code-block:: shell

   sudo -u ahriman ahriman repo-check

During the check process, the service will generate changes from the last known commit and will send it to remote service. In order to verify source files changes, the web interface or special subcommand can be used:

.. code-block:: shell

   ahriman package-changes ahriman

After validation, the operator can run update process with approved list of packages, e.g.:

.. code-block:: shell

   sudo -u ahriman ahriman repo-update ahriman

How to remove package
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-remove ahriman

Also, there is command ``repo-remove-unknown`` which checks packages in AUR and local storage and removes ones which have been removed.

Remove commands also remove any package files (patches, caches etc).

How to sign repository
^^^^^^^^^^^^^^^^^^^^^^

Repository sign feature is available in several configurations. The recommended way is just to sign repository database file by single key instead of trying to sign each package. However, the steps are pretty same, just configuration is a bit different. For more details about options kindly refer to :doc:`configuration reference </configuration>`.

#.
   First you would need to create the key on your local machine:

   .. code-block:: shell

      gpg --full-generate-key

   This command will prompt you for several questions. Most of them may be left default, but you will need to fill real name and email address with some data. Because at the moment the service doesn't support passphrases, it must be left blank.

#.
   The command above will generate key and print its fingerprint, something like ``8BE91E5A773FB48AC05CC1EDBED105AED6246B39``. Copy it.

#.
   Export your private key by using the fingerprint above:

   .. code-block:: shell

      gpg --export-secret-keys -a 8BE91E5A773FB48AC05CC1EDBED105AED6246B39 > repository-key.gpg

#.

   Copy the specified key to the build machine (i.e. where the service is running).

#.
   Import the specified key to the service user:

   .. code-block:: shell

      sudo -u ahriman gpg --import repository-key.gpg

   Don't forget to remove the key from filesystem after import.

#.
   Change trust level to ``ultimate``:

   .. code-block:: shell

      sudo -u ahriman gpg --edit-key 8BE91E5A773FB48AC05CC1EDBED105AED6246B39

   The command above will drop you into gpg shell, in which you will need to type ``trust``, choose ``5 = I trust ultimately``, confirm and exit ``quit``.

#.
   Proceed with service configuration according to the :doc:`configuration </configuration>`:

   .. code-block:: ini

      [sign]
      target = repository
      key = 8BE91E5A773FB48AC05CC1EDBED105AED6246B39


How to rebuild packages after library update
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman repo-rebuild --depends-on python

You can even rebuild the whole repository (which is particular useful in case if you would like to change packager) if you do not supply ``--depends-on`` option. This action will automatically increment ``pkgrel`` value; in case if you don't want to, the ``--no-increment`` option has to be supplied.

However, note that you do not need to rebuild repository in case if you just changed signing option, just use ``repo-sign`` command instead.

Automated broken dependencies detection
"""""""""""""""""""""""""""""""""""""""

After the success build the application extracts all linked libraries and used directories and stores them in database. During the check process, the application extracts pacman databases and checks if file names have been changed (e.g. new python release caused ``/usr/lib/python3.x`` directory renaming to ``/usr/lib/python3.y`` or soname for a linked library has been changed). In case if broken dependencies have been detected, the package will be added to the rebuild queue.

In order to disable this check completely, the ``--no-check-files`` flag can be used.

In addition, there is possibility to control paths which will be used for checking, by using option ``${build:scan_paths}``, which supports regular expressions. Leaving ``${build:scan_paths}`` blank will effectively disable any check too.

How to install built packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the following lines to your ``pacman.conf``:

.. code-block:: ini

   [repository]
   Server = file:///var/lib/ahriman/repository/$repo/$arch

(You might need to add ``SigLevel`` option according to the pacman documentation.)

How to serve repository
^^^^^^^^^^^^^^^^^^^^^^^

Easy. For example, nginx configuration (without SSL) will look like:

.. code-block::

   server {
       listen 80;
       server_name repo.example.com;

       location / {
           autoindex on;
           root /var/lib/ahriman/repository;
       }
   }

Example of the status page configuration is the following (status service is using 8080 port):

.. code-block::

   server {
       listen 80;
       server_name builds.example.com;

       location / {
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarder-Proto $scheme;

           proxy_pass http://127.0.0.1:8080;
       }
   }

Some more examples can be found in configuration `recipes <https://github.com/arcan1s/ahriman/tree/master/recipes>`__.
