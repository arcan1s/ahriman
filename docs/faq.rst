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
   ahriman -a x86_64 service-setup --packager "ahriman bot <ahriman@example.com>" --repository "repository"
   systemctl enable --now ahriman@x86_64.timer

Long answer
"""""""""""

The idea is to install the package as usual, create working directory tree, create configuration for ``sudo`` and ``devtools``. Detailed description of the setup instruction can be found :doc:`here <setup>`.

How to validate settings
^^^^^^^^^^^^^^^^^^^^^^^^

There is special command which can be used in order to validate current configuration:

.. code-block:: shell

   ahriman -a x86_64 service-config-validate --exit-code

This command will print found errors, based on `cerberus <https://docs.python-cerberus.org/>`_, e.g.:

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

the ``extra-i686-build`` command will be used for ``i686`` architecture.

How to generate build reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Normally you probably like to generate only one report for the specific type, e.g. only one email report. In order to do it you will need to have the following configuration:

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

How do I add new package
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman --now

``--now`` flag is totally optional and just run ``repo-update`` subcommand after the registering the new package, Thus the extended flow is the following:

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman
   sudo -u ahriman ahriman repo-update

How to build package from local PKGBUILD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman package-add /path/to/local/directory/with/PKGBUILD --now

Before using this command you will need to create local directory, put ``PKGBUILD`` there and generate ``.SRCINFO`` by using ``makepkg --printsrcinfo > .SRCINFO`` command. These packages will be stored locally and *will be ignored* during automatic update; in order to update the package you will need to run ``package-add`` command again.


How to fetch PKGBUILDs from remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you could use ``RemotePullTrigger`` trigger. To do so you will need to configure trigger as following:

.. code-block:: ini

   [remote-pull]
   target = gitremote

   [gitremote]
   pull_url = https://github.com/username/repository

During the next application run it will fetch repository from the specified url and will try to find packages there which can be used as local sources.

How to push updated PKGBUILDs to remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you'd need to use another trigger called ``RemotePushTrigger``. Configure trigger as following:

.. code-block:: ini

   [remote-push]
   target = gitremote

   [gitremote]
   push_url = https://github.com/username/repository

Unlike ``RemotePullTrigger`` trigger, the ``RemotePushTrigger`` more likely will require authorization. It is highly recommended to use application tokens for that instead of using your password (e.g. for Github you can generate tokens `here <https://github.com/settings/tokens>`_ with scope ``public_repo``). Authorization can be supplied by using authorization part of the url, e.g. ``https://key:token@github.com/username/repository``.

How to change PKGBUILDs before build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well it is supported also. The recommended way is to patch specific function, e.g. by running

.. code-block:: shell

   sudo -u ahriman ahriman patch-add ahriman version

This command will prompt for new value of the PKGBUILD variable ``version``. You can also write it to file and read from it:

.. code-block:: shell

   sudo -u ahriman ahriman patch-add ahriman version version.patch

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

How to build package from official repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So it is the same as adding any other package, but due to restrictions you must specify source explicitly, e.g.:

.. code-block:: shell

   sudo -u ahriman ahriman package-add pacman -s repository

This feature is heavily depends on local pacman cache. In order to use this feature it is recommended to either run ``pacman -Sy`` before the interaction or configure timer for this.

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

How to remove package
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-remove ahriman

Also, there is command ``repo-remove-unknown`` which checks packages in AUR and local storage and removes ones which have been removed.

Remove commands also remove any package files (patches, caches etc).

How to sign repository
^^^^^^^^^^^^^^^^^^^^^^

Repository sign feature is available in several configurations. The recommended way is just to sign repository database file by single key instead of trying to sign each package. However, the steps are pretty same, just configuration is a bit differ. For more details about options kindly refer to :doc:`configuration reference <configuration>`.

#.
   First you would need to create the key on your local machine:

   .. code-block:: shell

      gpg --full-generate-key

   This command will prompt you for several questions. Most of them may be left default, but you will need to fill real name and email address with some data. Because at the moment the service doesn't support passphrases, it must be left blank.

#.
   The command above will generate key and print its hash, something like ``8BE91E5A773FB48AC05CC1EDBED105AED6246B39``. Copy it.

#.
   Export your private key by using the hash above:

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
   Server = file:///var/lib/ahriman/repository/x86_64

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

Docker image
------------

We provide official images which can be found under ``arcan1s/ahriman`` repository. Docker image is being updated on each commit to master as well as on each version. If you would like to use last (probably unstable) build you can use ``edge`` tag or ``latest`` for any tagged versions; otherwise you can use any version tag available.

The default action (in case if no arguments provided) is ``repo-update``. Basically the idea is to run container, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

``--privileged`` flag is required to make mount possible inside container. In order to make data available outside of container, you would need to mount local (parent) directory inside container by using ``-v /path/to/local/repo:/var/lib/ahriman`` argument, where ``/path/to/local/repo`` is a path to repository on local machine. In addition, you can pass own configuration overrides by using the same ``-v`` flag, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman -v /path/to/overrides/overrides.ini:/etc/ahriman.ini.d/10-overrides.ini arcan1s/ahriman:latest

The action can be specified during run, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest package-add ahriman --now

For more details please refer to docker FAQ.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The following environment variables are supported:

* ``AHRIMAN_ARCHITECTURE`` - architecture of the repository, default is ``x86_64``.
* ``AHRIMAN_DEBUG`` - if set all commands will be logged to console.
* ``AHRIMAN_FORCE_ROOT`` - force run ahriman as root instead of guessing by subcommand.
* ``AHRIMAN_HOST`` - host for the web interface, default is ``0.0.0.0``.
* ``AHRIMAN_MULTILIB`` - if set (default) multilib repository will be used, disabled otherwise.
* ``AHRIMAN_OAUTH_CLIENT_ID`` - OAUTH client ID.
* ``AHRIMAN_OAUTH_CLIENT_SECRET`` - OAUTH client secret.
* ``AHRIMAN_OAUTH_ENABLE`` - enable configuration of OAUTH, needs all other ``_OAUTH_`` variables to be set as well.
* ``AHRIMAN_OAUTH_PROVIDER`` - OAUTH provider, defaults to ``GithubClient``.
* ``AHRIMAN_OAUTH_SCOPE`` - Scope to be used by OAUTH provider.
* ``AHRIMAN_OUTPUT`` - controls logging handler, e.g. ``syslog``, ``console``. The name must be found in logging configuration. Note that if ``syslog`` handler is used you will need to mount ``/dev/log`` inside container because it is not available there.
* ``AHRIMAN_PACKAGER`` - packager name from which packages will be built, default is ``ahriman bot <ahriman@example.com>``.
* ``AHRIMAN_PACMAN_MIRROR`` - override pacman mirror server if set.
* ``AHRIMAN_PORT`` - HTTP server port if any, default is empty.
* ``AHRIMAN_REPORT_TELEGRAM`` - posts update notifications to Telegram channels if enabled. Needs to be supplied with secrets as well.
* ``AHRIMAN_REPOSITORY_ROOT`` - repository root. Because of filesystem rights it is required to override default repository root. By default, it uses ``ahriman`` directory inside ahriman's home, which can be passed as mount volume.
* ``AHRIMAN_REPOSITORY`` - repository name, default is ``aur-clone``.
* ``AHRIMAN_TELEGRAM_API_KEY`` - sets Telegram API key obtained by botfather.
* ``AHRIMAN_TELEGRAM_CHAT_ID`` - where to post notifications in Telegram.
* ``AHRIMAN_UNIX_SOCKET`` - full path to unix socket which is used by web server, default is empty. Note that more likely you would like to put it inside ``AHRIMAN_REPOSITORY_ROOT`` directory (e.g. ``/var/lib/ahriman/ahriman/ahriman-web.sock``) or to ``/tmp``.
* ``AHRIMAN_USER`` - ahriman user, usually must not be overwritten, default is ``ahriman``.
* ``AHRIMAN_VALIDATE_CONFIGURATION`` - if set validate service configuration.

You can pass any of these variables by using ``-e`` argument, e.g.:

.. code-block:: shell

   docker run --privileged -e AHRIMAN_PORT=8080 -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Daemon service
^^^^^^^^^^^^^^

There is special ``repo-daemon`` subcommand which emulates systemd timer and will perform repository update periodically:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest repo-daemon

This command uses same rules as ``repo-update``, thus, e.g. requires ``--privileged`` flag.

Web service setup
^^^^^^^^^^^^^^^^^

Well for that you would need to have web container instance running forever; it can be achieved by the following command:

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


Non-x86_64 architecture setup
-----------------------------

The following section describes how to setup ahriman with architecture different from x86_64, as example i686. For most cases you have base repository available, e.g. archlinux32 repositories for i686 architecture; in case if base repository is not available, steps are a bit different, however, idea remains the same.

Physical server setup
^^^^^^^^^^^^^^^^^^^^^

In this example we are going to use files and packages which are provided by official repositories of the used architecture. Note, that versions might be different, thus you need to find correct versions on the distribution web site, e.g. `archlinux32 packages <https://www.archlinux32.org/packages/>`_.

#.
   First, considering having base Arch Linux system, we need to install keyring for the specified repositories:

   .. code-block:: shell

      wget http://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20220927-1.0-any.pkg.tar.zst
      pacman -U archlinux32-keyring-20220927-1.0-any.pkg.tar.zst

#.
   In order to run ``devtools`` scripts for custom architecture they also need specific ``makepkg`` configuration, it can be retrieved by installing the ``devtools`` package of the distribution:

   .. code-block:: shell

      wget http://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.0-any.pkg.tar.zst
      pacman -U devtools-20221208-1.0-any.pkg.tar.zst

   Alternatively, you can create your own ``makepkg`` configuration and save it as ``/usr/share/devtools/makepkg-i686.conf``.

#.
   Setup repository as usual:

   .. code-block:: shell

      ahriman -a i686 service-setup --mirror 'http://de.mirror.archlinux32.org/$arch/$repo'--no-multilib ...

   In addition to usual options, you need to specify the following options:

   * ``--mirror`` - link to the mirrors which will be used instead of official repositories.
   * ``--no-multilib`` - in the example we are using i686 architecture for which multilib repository doesn't exist.

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
      RUN wget http://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.0-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.0-any.pkg.tar.zst
      RUN wget http://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20220927-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20220927-1.0-any.pkg.tar.zst

#.
   At that point you should have full ``Dockerfile`` like:

   .. code-block:: dockerfile

      FROM arcan1s/ahriman:latest

      RUN pacman-key --init

      RUN pacman --noconfirm -Sy wget
      RUN wget http://pool.mirror.archlinux32.org/i686/extra/devtools-20221208-1.0-any.pkg.tar.zst && pacman --noconfirm -U devtools-20221208-1.0-any.pkg.tar.zst
      RUN wget http://pool.mirror.archlinux32.org/i686/core/archlinux32-keyring-20220927-1.0-any.pkg.tar.zst && pacman --noconfirm -U archlinux32-keyring-20220927-1.0-any.pkg.tar.zst

#.
   After that you can build you own container, e.g.:

   .. code-block:: shell

      docker build --tag ahriman-i686:latest

#.
   Now you can run locally built container as usual with passing environment variables for setup command:

   .. code-block:: shell

      docker run --privileged -p 8080:8080 -e AHRIMAN_ARCHITECTURE=i686 -e AHRIMAN_PACMAN_MIRROR='http://de.mirror.archlinux32.org/$arch/$repo' -e AHRIMAN_MULTILIB= ahriman-i686:latest

Remote synchronization
----------------------

How to sync repository to another server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several choices:

#. 
   Easy and cheap, just share your local files through the internet, e.g. for ``nginx``:

   .. code-block::

       server {
           location /x86_64 {
               root /var/lib/ahriman/repository/x86_64;
               autoindex on;
           }
       }

#. 
   You can also upload your packages using ``rsync`` to any available server. In order to use it you would need to configure ahriman first:

   .. code-block:: ini

       [upload]
       target = rsync

       [rsync]
       remote = 192.168.0.1:/srv/repo

   After that just add ``/srv/repo`` to the ``pacman.conf`` as usual. You can also upload to S3 (e.g. ``Server = https://s3.eu-central-1.amazonaws.com/repository/x86_64``) or to Github (e.g. ``Server = https://github.com/ahriman/repository/releases/download/x86_64``).

How to sync to S3
^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      pacman -S python-boto3

#. 
   Create a bucket.

#. 
   Create user with write access to the bucket:

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

How to sync to Github releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Create a repository.
#. 
   `Create API key <https://github.com/settings/tokens>`_ with scope ``public_repo``.
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
      link_path = http://example.com/x86_64
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
      path = /var/lib/ahriman/repository/x86_64/index.html
      link_path = http://example.com/x86_64

After these steps ``index.html`` file will be automatically synced to S3

How to post build report to telegram
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   It still requires additional dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#. 
   Register bot in telegram. You can do it by talking with `@BotFather <https://t.me/botfather>`_. For more details please refer to `official documentation <https://core.telegram.org/bots>`_.

#. 
   Optionally (if you want to post message in chat):


   #. Create telegram channel. 
   #. Invite your bot into the channel.
   #. Make your channel public

#. 
   Get chat id if you want to use by numerical id or just use id prefixed with ``@`` (e.g. ``@ahriman``). If you are not using chat the chat id is your user id. If you don't want to make channel public you can use `this guide <https://stackoverflow.com/a/33862907>`_.

#. 
   Configure the service:

   .. code-block:: ini

      [report]
      target = telegram

      [telegram]
      api_key = aaAAbbBBccCC
      chat_id = @ahriman
      link_path = http://example.com/x86_64

   ``api_key`` is the one sent by `@BotFather <https://t.me/botfather>`_, ``chat_id`` is the value retrieved from previous step.

If you did everything fine you should receive the message with the next update. Quick credentials check can be done by using the following command:

.. code-block:: shell

   curl 'https://api.telegram.org/bot${CHAT_ID}/sendMessage?chat_id=${API_KEY}&text=hello'

(replace ``${CHAT_ID}`` and ``${API_KEY}`` with the values from configuration).

Maintenance packages
--------------------

Generate keyring package
^^^^^^^^^^^^^^^^^^^^^^^^

The application provides special plugin which generates keyring package. This plugin heavily depends on ``sign`` group settings, however it is possible to override them. The minimal package can be generated in the following way:

#.
   Edit configuration:

   .. code-block:: ini

      [keyring]
      target = keyring_generator

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

This plugin might have some issues, in case of any of them, kindly create `new issue <https://github.com/arcan1s/ahriman/issues/new/choose>`_.

Generate mirrorlist package
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application provides special plugin which generates mirrorlist package also. It is possible to distribute this package as usual later. The package can be generated in the following way:

#.
   Edit configuration:

   .. code-block:: ini

      [mirrorlist]
      target = mirrorlist_generator

      [mirrorlist_generator]
      servers = https://repo.example.com/$arch

   The ``mirrorlist_generator.servers`` must contain list of available mirrors, the ``$arch`` and ``$repo`` variables are supported. For more options kindly refer to :doc:`configuration <configuration>`.

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
   Start the web service ``systemctl enable --now ahriman-web@x86_64``.

How to enable basic authorization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies 😊:

   .. code-block:: shell

      yay -S --asdeps python-aiohttp-security python-aiohttp-session python-cryptography

#. 
   Configure the service to enable authorization (``salt`` can be generated as any random string):

   .. code-block:: ini

      [auth]
      target = configuration
      salt = somerandomstring

   The ``salt`` parameter is optional, but recommended.

#.
   In order to provide access for reporting from application instances you can (recommended way) use unix sockets by configuring the following (note, that it requires ``python-requests-unixsocket`` package to be installed):

   .. code-block:: ini

      [web]
      unix_socket = /var/lib/ahriman/ahriman-web.sock

   This socket path must be available for web service instance and must be available for application instances (e.g. in case if you are using docker container, see above, you need to be sure that the socket is passed to the root filesystem).

   By the way, unix socket variable will be automatically set in case if ``--web-unix-socket`` argument is supplied to the ``setup`` subcommand.

   Alternatively, you need to create user for the service:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add -r full api

   This command will ask for the password, just type it in stdin; *do not* leave the field blank, user will not be able to authorize, and finally configure the application:

   .. code-block:: ini

      [web]
      username = api
      password = pa55w0rd

#.
   Create end-user with password:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add -r full my-first-user

#.
   Restart web service ``systemctl restart ahriman-web@x86_64``.

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
   Restart web service ``systemctl restart ahriman-web@x86_64``.

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

Other topics
------------

How does it differ from %another-manager%?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Short answer - I do not know. Also for some references credits to `Alad <https://github.com/AladW>`_, he `did <https://wiki.archlinux.org/title/User:Alad/Local_repo_tools>`_ really good investigation of existing alternatives.

`arch-repo-manager <https://github.com/Martchus/arch-repo-manager>`_
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Looks actually pretty good, in case if I would find it, I would probably didn't start this project, most of features (like web interface or additional helpers) are already implemented or planned to be. However, this project seems to be at early alpha stage (as for Nov 2022), written in C++ (not pro or con) and misses code documentation.

`archrepo2 <https://github.com/lilydjwg/archrepo2>`_
""""""""""""""""""""""""""""""""""""""""""""""""""""

Don't know, haven't tried it. But it lacks of documentation at least.

* ``ahriman`` has web interface.
* ``archrepo2`` doesn't have synchronization and reporting.
* ``archrepo2`` actively uses direct shell calls and ``yaourt`` components.
* ``archrepo2`` has constantly running process instead of timer process (it is not pro or con).

`repoctl <https://github.com/cassava/repoctl>`_
"""""""""""""""""""""""""""""""""""""""""""""""

* ``ahriman`` has web interface.
* ``repoctl`` does not have reporting feature.
* ``repoctl`` does not support local packages and patches.
* Some actions are not fully automated in ``repoctl`` (e.g. package update still requires manual intervention for the build itself).
* ``repoctl`` has better AUR interaction features. With colors!
* ``repoctl`` has much easier configuration and even completion.
* ``repoctl`` is able to store old packages.
* Ability to host repository from same command in ``repoctl`` vs external services (e.g. nginx) in ``ahriman``.

`repod <https://gitlab.archlinux.org/archlinux/repod>`_
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

Official tool provided by distribution, has clean logic, but it is just a helper for ``repo-add``, e.g. it doesn't work with AUR and all packages builds have to be handled separately.

`repo-scripts <https://github.com/arcan1s/repo-scripts>`_
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Though originally I've created ahriman by trying to improve the project, it still lacks a lot of features:

* ``ahriman`` has web interface.
* ``ahriman`` has better reporting with template support.
* ``ahriman`` has more synchronization features (there was only ``rsync`` based).
* ``ahriman`` supports local packages and patches.
* ``repo-scripts`` doesn't have dependency management.

...and so on. ``repo-scripts`` also has bad architecture and bad quality code and uses out-of-dated ``yaourt`` and ``package-query``.

`toolbox <https://github.com/chaotic-aur/toolbox>`_
"""""""""""""""""""""""""""""""""""""""""""""""""""

It is automation tools for ``repoctl`` mentioned above. Except for using shell it looks pretty cool and also offers some additional features like patches, remote synchronization (isn't it?) and reporting.

How to check service logs
^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the service writes logs to ``journald`` which can be accessed by using ``journalctl`` command (logs are written to the journal of the user under which command is run). In order to retrieve logs for the process you can use the following command:

.. code-block:: shell

   sudo journalctl SYSLOG_IDENTIFIER=ahriman

You can also ask to forward logs to ``stderr``, just set ``--log-handler`` flag, e.g.:

.. code-block:: shell

   ahriman --log-handler console ...

You can even configure logging as you wish, but kindly refer to python ``logging`` module `configuration <https://docs.python.org/3/library/logging.config.html>`_. The application uses java concept to log messages, e.g. class ``Application`` imported from ``ahriman.application.application`` package will have logger called ``ahriman.application.application.Application``. In order to e.g. change logger name for whole application package it is possible to change values for ``ahriman.application`` package; thus editing ``ahriman`` logger configuration will change logging for whole application (unless there are overrides for another logger).

Html customization
^^^^^^^^^^^^^^^^^^

It is possible to customize html templates. In order to do so, create files somewhere (refer to Jinja2 documentation and the service source code for available parameters) and put ``template_path`` to configuration pointing to this directory.

I did not find my question
^^^^^^^^^^^^^^^^^^^^^^^^^^

`Create an issue <https://github.com/arcan1s/ahriman/issues>`_ with type **Question**.
