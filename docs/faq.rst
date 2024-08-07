FAQ
===

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

The idea is to install the package as usual, create working directory tree, create configuration for ``sudo`` and ``devtools``. Detailed description of the setup instruction can be found :doc:`here <setup>`.

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

Before using this command you will need to create local directory, put ``PKGBUILD`` there and generate ``.SRCINFO`` by using ``makepkg --printsrcinfo > .SRCINFO`` command. These packages will be stored locally and *will be ignored* during automatic update; in order to update the package you will need to run ``package-add`` command again.

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

Normally the service handles VCS packages correctly, however it requires additional dependencies:

.. code-block:: shell

   pacman -S breezy darcs mercurial subversion

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

Repository sign feature is available in several configurations. The recommended way is just to sign repository database file by single key instead of trying to sign each package. However, the steps are pretty same, just configuration is a bit different. For more details about options kindly refer to :doc:`configuration reference <configuration>`.

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
   Proceed with service configuration according to the :doc:`configuration <configuration>`:

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

Non-x86_64 architecture setup
-----------------------------

The following section describes how to setup ahriman with architecture different from x86_64, as example i686. For most cases you have base repository available, e.g. archlinux32 repositories for i686 architecture; in case if base repository is not available, steps are a bit different, however, idea remains the same.

The example of setup with docker compose can be found `here <https://github.com/arcan1s/ahriman/tree/master/recipes/i686>`__.

Physical server setup
^^^^^^^^^^^^^^^^^^^^^

In this example we are going to use files and packages which are provided by official repositories of the used architecture. Note, that versions might be different, thus you need to find correct versions on the distribution web site, e.g. `archlinux32 packages <https://www.archlinux32.org/packages/>`__.

#.
   First, considering having base Arch Linux system, we need to install keyring for the specified repositories, e.g.:

   .. code-block:: shell

      wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst
      pacman -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   In order to run ``devtools`` scripts for custom architecture they also need specific ``makepkg`` configuration, it can be retrieved by installing the ``devtools`` package of the distribution, e.g.:

   .. code-block:: shell

      wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst
      pacman -U devtools-20221208-1.2-any.pkg.tar.zst

   Alternatively, you can create your own ``makepkg`` configuration and save it as ``/usr/share/devtools/makepkg.conf.d/i686.conf``.

#.
   Setup repository as usual:

   .. code-block:: shell

      ahriman -a i686 service-setup --mirror 'https://de.mirror.archlinux32.org/$arch/$repo'--no-multilib ...

   In addition to usual options, you need to specify the following options:

   * ``--mirror`` - link to the mirrors which will be used instead of official repositories.
   * ``--no-multilib`` - in the example we are using i686 architecture for which multilib repository doesn't exist.

#.
   That's all Folks!

Docker container setup
^^^^^^^^^^^^^^^^^^^^^^

There are two possible ways to achieve same setup, by using docker container. The first one is just mount required files inside container and run it as usual (with specific environment variables). Another one is to create own container based on official one:

#.
   Clone official container as base:

   .. code-block:: dockerfile

      FROM arcan1s/ahriman:latest

#.
   Init pacman keys. This command is required in order to populate distribution keys:

   .. code-block:: dockerfile

      RUN pacman-key --init

#.
   Install packages as it was described above:

   .. code-block:: dockerfile

      RUN pacman --noconfirm -Sy wget
      RUN wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.2-any.pkg.tar.zst
      RUN wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   At that point you should have full ``Dockerfile`` like:

   .. code-block:: dockerfile

      FROM arcan1s/ahriman:latest

      RUN pacman-key --init

      RUN pacman --noconfirm -Sy wget
      RUN wget https://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.2-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.2-any.pkg.tar.zst
      RUN wget https://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20230705-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20230705-1.0-any.pkg.tar.zst

#.
   After that you can build you own container, e.g.:

   .. code-block:: shell

      docker build --tag ahriman-i686:latest

#.
   Now you can run locally built container as usual with passing environment variables for setup command:

   .. code-block:: shell

      docker run --privileged -p 8080:8080 -e AHRIMAN_ARCHITECTURE=i686 -e AHRIMAN_PACMAN_MIRROR='https://de.mirror.archlinux32.org/$arch/$repo' -e AHRIMAN_MULTILIB= ahriman-i686:latest

Remote synchronization
----------------------

How to sync repository to another server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several choices:

#. 
   Easy and cheap, just share your local files through the internet, e.g. for ``nginx``:

   .. code-block::

       server {
           location / {
               autoindex on;
               root /var/lib/ahriman/repository/;
           }
       }

#. 
   You can also upload your packages using ``rsync`` to any available server. In order to use it you would need to configure ahriman first:

   .. code-block:: ini

       [upload]
       target = rsync

       [rsync]
       remote = 192.168.0.1:/srv/repo

   After that just add ``/srv/repo`` to the ``pacman.conf`` as usual. You can also upload to S3 (``Server = https://s3.eu-central-1.amazonaws.com/repository/aur-clone/x86_64``) or to GitHub (``Server = https://github.com/ahriman/repository/releases/download/aur-clone-x86_64``).

How to sync to S3
^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      pacman -S python-boto3

#. 
   Create a bucket (e.g. ``repository``).

#. 
   Create an user with write access to the bucket:

   .. code-block::

       {
           "Version": "2012-10-17",
           "Statement": [
               {
                   "Sid": "ListObjectsInBucket",
                   "Effect": "Allow",
                   "Action": [
                       "s3:ListBucket"
                   ],
                   "Resource": [
                       "arn:aws:s3:::repository"
                   ]
               },
               {
                   "Sid": "AllObjectActions",
                   "Effect": "Allow",
                   "Action": "s3:*Object",
                   "Resource": [
                       "arn:aws:s3:::repository/*"
                   ]
               }
           ]
       }

#. 
   Create an API key for the user and store it.

#. 
   Configure the service as following:

   .. code-block:: ini

       [upload]
       target = s3

       [s3]
       access_key = ...
       bucket = repository
       region = eu-central-1
       secret_key = ...

S3 with SSL
"""""""""""

In order to configure S3 on custom domain with SSL (and some other features, like redirects), the CloudFront should be used.

#. Configure S3 as described above.
#. In bucket properties, enable static website hosting with hosting type "Host a static website".
#. Go to AWS Certificate Manager and create public certificate on your domain. Validate domain as suggested.
#. Go to CloudFront and create distribution. The following settings are required:

   * Origin domain choose S3 bucket.
   * Tick use website endpoint.
   * Disable caching.
   * Select issued certificate.

#. Point DNS record to CloudFront address.

How to sync to GitHub releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Create a repository.

#.
   `Create API key <https://github.com/settings/tokens>`__ with scope ``public_repo``.

#.
   Configure the service as following:

   .. code-block:: ini

       [upload]
       target = github

       [github]
       owner = ahriman
       password = ...
       repository = repository
       username = ahriman

Reporting
---------

How to report by email
^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#. 
   Configure the service:

   .. code-block:: ini

      [report]
      target = email

      [email]
      host = smtp.example.com
      link_path = http://example.com/aur-clone/x86_64
      password = ...
      port = 465
      receivers = me@example.com
      sender = me@example.com
      user = me@example.com

How to generate index page for S3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#. 
   Configure the service:

   .. code-block:: ini

      [report]
      target = html

      [html]
      path = /var/lib/ahriman/repository/aur-clone/x86_64/index.html
      link_path = http://example.com/aur-clone/x86_64

After these steps ``index.html`` file will be automatically synced to S3.

How to post build report to telegram
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   It still requires additional dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#. 
   Register bot in telegram. You can do it by starting chat with `@BotFather <https://t.me/botfather>`__. For more details please refer to `official documentation <https://core.telegram.org/bots>`__.

#. 
   Optionally (if you want to post message in chat):

   #. Create telegram channel.
   #. Invite your bot into the channel.
   #. Make your channel public

#. 
   Get chat id if you want to use by numerical id or just use id prefixed with ``@`` (e.g. ``@ahriman``). If you are not using chat the chat id is your user id. If you don't want to make channel public you can use `this guide <https://stackoverflow.com/a/33862907>`__.

#. 
   Configure the service:

   .. code-block:: ini

      [report]
      target = telegram

      [telegram]
      api_key = aaAAbbBBccCC
      chat_id = @ahriman
      link_path = http://example.com/aur-clone/x86_64

   ``api_key`` is the one sent by `@BotFather <https://t.me/botfather>`__, ``chat_id`` is the value retrieved from previous step.

If you did everything fine you should receive the message with the next update. Quick credentials check can be done by using the following command:

.. code-block:: shell

   curl 'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text=hello'

(replace ``{chat_id}`` and ``{api_key}`` with the values from configuration).

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
  As it has been mentioned above, it is recommended to enable authentication (see `How to enable basic authorization`_) and create system user which will be used later. Later this user (if any) will be referenced as ``worker-user``.

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

.. code-block:: ini

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

Maintenance packages
--------------------

Generate keyring package
^^^^^^^^^^^^^^^^^^^^^^^^

The application provides special plugin which generates keyring package. This plugin heavily depends on ``sign`` group settings, however it is possible to override them. The minimal package can be generated in the following way:

#.
   Edit configuration:

   .. code-block:: ini

      [keyring]
      target = keyring-generator

   By default it will use ``sign.key`` as trusted key and all other keys as packagers ones. For all available options refer to :doc:`configuration <configuration>`.

#.
   Create package source files:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-create-keyring

   This command will generate PKGBUILD, revoked and trusted listings and keyring itself and will register the package in database.

#.
   Build new package as usual:

   .. code-block:: shell

      sudo -u ahriman ahriman package-add aur-clone-keyring --source local --now

   where ``aur-clone`` is your repository name.

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

   The ``mirrorlist-generator.servers`` must contain list of available mirrors, the ``$arch`` and ``$repo`` variables are supported. For more options kindly refer to :doc:`configuration <configuration>`.

#.
   Create package source files:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-create-mirrorlist

   This command will generate PKGBUILD and mirrorlist file and will register the package in database.

#.
   Build new package as usual:

   .. code-block:: shell

      sudo -u ahriman ahriman package-add aur-clone-mirrorlist --source local --now

   where ``aur-clone`` is your repository name.

Web service
-----------

How to setup web service
^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-aiohttp python-aiohttp-jinja2 python-aiohttp-apispec>=3.0.0 python-aiohttp-cors

#. 
   Configure service:

   .. code-block:: ini

      [web]
      port = 8080

#. 
   Start the web service ``systemctl enable --now ahriman-web``.

How to enable basic authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies 😊:

   .. code-block:: shell

      yay -S --asdeps python-aiohttp-security python-aiohttp-session python-cryptography

#. 
   Configure the service to enable authorization:

   .. code-block:: ini

      [auth]
      target = configuration
      salt = somerandomstring

   The ``salt`` parameter is optional, but recommended, and can be set to any (random) string.

#.
   In order to provide access for reporting from application instances you can (the recommended way) use unix sockets by the following configuration (note, that it requires ``python-requests-unixsocket2`` package to be installed):

   .. code-block:: ini

      [web]
      unix_socket = /run/ahriman/ahriman-web.sock

   This socket path must be available for web service instance and must be available for all application instances (e.g. in case if you are using docker container - see above - you need to make sure that the socket is passed to the root filesystem).

   By the way, unix socket variable will be automatically set in case if ``--web-unix-socket`` argument is supplied to the ``setup`` subcommand.

   Alternatively, you need to create user for the service:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add -r full api

   This command will ask for the password, just type it in stdin; **do not** leave the field blank, user will not be able to authorize, and finally configure the application:

   .. code-block:: ini

      [status]
      username = api
      password = pa55w0rd

#.
   Create end-user with password:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add -r full my-first-user

#.
   Restart web service ``systemctl restart ahriman-web``.

How to enable OAuth authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Create OAuth web application, download its ``client_id`` and ``client_secret``.

#.
   Guess what? Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-aiohttp-security python-aiohttp-session python-cryptography python-aioauth-client

#. 
   Configure the service:

   .. code-block:: ini

      [auth]
      target = oauth
      client_id = ...
      client_secret = ...

      [web]
      address = https://example.com

   Configure ``oauth_provider`` and ``oauth_scopes`` in case if you would like to use different from Google provider. Scope must grant access to user email. ``web.address`` is required to make callback URL available from internet.

#. 
   If you are not going to use unix socket, you also need to create service user (remember to set ``auth.salt`` option before if required):

   .. code-block:: shell

      sudo -u ahriman ahriman user-add --as-service -r full api

#. 
   Create end-user:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add -r full my-first-user

   When it will ask for the password leave it blank.

#.
   Restart web service ``systemctl restart ahriman-web``.

How to implement own interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can write your own interface by using API which is provided by the web service. Full autogenerated API documentation is available at ``http://localhost:8080/api-docs``.

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

Use cases
---------

There is a collection of some specific recipes which can be found in `the repository <https://github.com/arcan1s/ahriman/tree/master/recipes>`__.

Most of them can be run (``AHRIMAN_PASSWORD`` environment variable is required in the most setups) as simple as:

.. code-block:: shell

   AHRIMAN_PASSWORD=demo docker compose up

Note, however, they are just an examples of specific configuration for specific cases and they are never intended to be used as is in real environment.

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
