FAQ
===

General topics
--------------

What is the purpose of the project?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project has been created in order to maintain self-hosted Arch Linux user repository without manual intervention - checking for updates and building packages.

How do I install it?
^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   yay -S ahriman
   sudo ahriman -a x86_64 repo-setup --packager "ahriman bot <ahriman@example.com>" --repository "repository"
   systemctl enable --now ahriman@x86_64.timer

Long answer
"""""""""""

The idea is to install the package as usual, create working directory tree, create configuration for ``sudo`` and ``devtools``. Detailed description of the setup instruction can be found :doc:`here <setup>`.

What does "architecture specific" mean? / How to configure for different architectures?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

How to use reporter/upload settings?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

Okay, I've installed ahriman, how do I add new package?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman --now

``--now`` flag is totally optional and just run ``repo-update`` subcommand after the registering the new package, Thus the extended flow is the following:

.. code-block:: shell

   sudo -u ahriman ahriman package-add ahriman
   sudo -u ahriman ahriman repo-update

AUR is fine, but I would like to create package from local PKGBUILD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman package-add /path/to/local/directory/with/PKGBUILD --now

Before using this command you will need to create local directory, put ``PKGBUILD`` there and generate ``.SRCINFO`` by using ``makepkg --printsrcinfo > .SRCINFO`` command. These packages will be stored locally and *will be ignored* during automatic update; in order to update the package you will need to run ``package-add`` command again.


Err, I have remote repository with PKGBUILDs and would like to get versions from there automatically
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you could use ``RemotePullTrigger`` trigger. To do so you will need:

#.
   Append ``triggers`` option in ``build`` section with the following line:

   .. code-block:: ini

      [build]
      triggers = ahriman.core.gitremote.RemotePullTrigger

#.
   Configure trigger as following:

   .. code-block:: ini

      [gitremote]
      pull_url = https://github.com/username/repository

During the next application run it will fetch repository from the specified url and will try to find packages there which can be used as local sources.

I would like to push PKGBUILDs to the remote repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For that purpose you'd need to use another trigger called ``RemotePushTrigger``. Configure it as following:

#.
   Append ``triggers`` option in ``build`` section with the trigger name:

   .. code-block:: ini

      [build]
      triggers = ahriman.core.gitremote.RemotePushTrigger

#.
   Configure trigger as following:

   .. code-block:: ini

      [gitremote]
      push_url = https://github.com/username/repository

Unlike ``RemotePullTrigger`` trigger, the ``RemotePushTrigger`` more likely will require authorization. It is highly recommended to use application tokens for that instead of using your password (e.g. for Github you can generate tokens `here <https://github.com/settings/tokens>`_ with scope ``public_repo``). Authorization can be supplied by using authorization part of the url, e.g. ``https://key:token@github.com/username/repository``.

But I just wanted to change PKGBUILD from AUR a bit!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well it is supported also.

#. Clone sources from AUR.
#. Make changes you would like to (e.g. edit ``PKGBUILD``, add external patches).
#. Run ``sudo -u ahriman ahriman patch-add /path/to/local/directory/with/PKGBUILD``.

The last command will calculate diff from current tree to the ``HEAD`` and will store it locally. Patches will be applied on any package actions (e.g. it can be used for dependency management).

Hey, I would like to rebuild the official repository package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So it is the same as adding any other package, but due to restrictions you must specify source explicitly, e.g.:

.. code-block:: shell

   sudo -u ahriman ahriman package-add pacman -s repository

This feature is heavily depends on local pacman cache. In order to use this feature it is recommended to either run ``pacman -Sy`` before the interaction or configure timer for this.

Package build fails because it cannot validate PGP signature of source files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman key-import ...

How do I check if there are new commits for VCS packages?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Normally the service handles VCS packages correctly, but it requires additional dependencies:

.. code-block:: shell

   pacman -S breezy darcs mercurial subversion

I would like to remove package because it is no longer needed/moved to official repositories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   sudo -u ahriman ahriman package-remove ahriman

Also, there is command ``repo-remove-unknown`` which checks packages in AUR and local storage and removes ones which have been removed.

Remove commands also remove any package files (patches, caches etc).

There is new major release of %library-name%, how do I rebuild packages?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TL;DR

.. code-block:: shell

   sudo -u ahriman ahriman repo-rebuild --depends-on python

You can even rebuild the whole repository (which is particular useful in case if you would like to change packager) if you do not supply ``--depends-on`` option.

However, note that you do not need to rebuild repository in case if you just changed signing option, just use ``repo-sign`` command instead. 

Hmm, I have packages built, but how can I use it?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the following lines to your ``pacman.conf``:

.. code-block:: ini

   [repository]
   Server = file:///var/lib/ahriman/repository/x86_64

(You might need to add ``SigLevel`` option according to the pacman documentation.)

I would like to serve the repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

We provide official images which can be found under ``arcan1s/ahriman`` repository. Docker image is being updated on each master commit as well as on each version. If you would like to use last (probably unstable) build you can use ``edge`` tag or ``latest`` for any tagged versions; otherwise you can use any version tag available. 

The default action (in case if no arguments provided) is ``repo-update``. Basically the idea is to run container, e.g.:

.. code-block:: shell

   docker run --privileged -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

``--privileged`` flag is required to make mount possible inside container. In addition, you can pass own configuration overrides by using the same ``-v`` flag, e.g.:

.. code-block:: shell

   docker run -v /path/to/local/repo:/var/lib/ahriman -v /etc/ahriman.ini:/etc/ahriman.ini.d/10-overrides.ini arcan1s/ahriman:latest

The action can be specified during run, e.g.:

.. code-block:: shell

   docker run arcan1s/ahriman:latest package-add ahriman --now

For more details please refer to docker FAQ.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

The following environment variables are supported:

* ``AHRIMAN_ARCHITECTURE`` - architecture of the repository, default is ``x86_64``.
* ``AHRIMAN_DEBUG`` - if set all commands will be logged to console.
* ``AHRIMAN_FORCE_ROOT`` - force run ahriman as root instead of guessing by subcommand.
* ``AHRIMAN_HOST`` - host for the web interface, default is ``0.0.0.0``.
* ``AHRIMAN_OUTPUT`` - controls logging handler, e.g. ``syslog``, ``console``. The name must be found in logging configuration. Note that if ``syslog`` (the default) handler is used you will need to mount ``/dev/log`` inside container because it is not available there.
* ``AHRIMAN_PACKAGER`` - packager name from which packages will be built, default is ``ahriman bot <ahriman@example.com>``.
* ``AHRIMAN_PORT`` - HTTP server port if any, default is empty.
* ``AHRIMAN_REPOSITORY`` - repository name, default is ``aur-clone``.
* ``AHRIMAN_REPOSITORY_ROOT`` - repository root. Because of filesystem rights it is required to override default repository root. By default, it uses ``ahriman`` directory inside ahriman's home, which can be passed as mount volume.
* ``AHRIMAN_USER`` - ahriman user, usually must not be overwritten, default is ``ahriman``. 

You can pass any of these variables by using ``-e`` argument, e.g.:

.. code-block:: shell

   docker run -e AHRIMAN_PORT=8080 arcan1s/ahriman:latest

Web service setup
^^^^^^^^^^^^^^^^^

Well for that you would need to have web container instance running forever; it can be achieved by the following command:

.. code-block:: shell

   docker run -p 8080:8080 -e AHRIMAN_PORT=8080 -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Note about ``AHRIMAN_PORT`` environment variable which is required in order to enable web service. An additional port bind by ``-p 8080:8080`` is required to pass docker port outside of container.

For every next container run use arguments ``-e AHRIMAN_PORT=8080 --net=host``, e.g.:

.. code-block:: shell

   docker run --privileged -e AHRIMAN_PORT=8080 --net=host -v /path/to/local/repo:/var/lib/ahriman arcan1s/ahriman:latest

Remote synchronization
----------------------

Wait I would like to use the repository from another server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

How do I configure S3?
^^^^^^^^^^^^^^^^^^^^^^

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

How do I configure Github?
^^^^^^^^^^^^^^^^^^^^^^^^^^

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

I would like to get report to email
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S python-jinja

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

I'm using synchronization to S3 and would like to generate index page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S python-jinja

#. 
   Configure the service:

   .. code-block:: ini

      [report]
      target = html

      [html]
      path = /var/lib/ahriman/repository/x86_64/index.html
      link_path = http://example.com/x86_64

After these steps ``index.html`` file will be automatically synced to S3

I would like to get messages to my telegram account/channel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   It still requires additional dependencies:

   .. code-block:: shell

      yay -S python-jinja

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

Web service
-----------

Readme mentions web interface, how do I use it?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies:

   .. code-block:: shell

      yay -S python-aiohttp python-aiohttp-jinja2

#. 
   Configure service:

   .. code-block:: ini

      [web]
      port = 8080

#. 
   Start the web service ``systemctl enable --now ahriman-web@x86_64``.

I would like to limit user access to the status page
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Install dependencies 😊:

   .. code-block:: shell

      yay -S python-aiohttp-security python-aiohttp-session python-cryptography

#. 
   Configure the service to enable authorization:

   .. code-block:: ini

      [auth]
      target = configuration

#. 
   Create user for the service:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add --as-service -r write api

   This command will ask for the password, just type it in stdin; *do not* leave the field blank, user will not be able to authorize.

#. 
   Create end-user ``sudo -u ahriman ahriman user-add -r write my-first-user`` with password.

#. Restart web service ``systemctl restart ahriman-web@x86_64``.

I would like to use OAuth
^^^^^^^^^^^^^^^^^^^^^^^^^

#. 
   Create OAuth web application, download its ``client_id`` and ``client_secret``.
#. 
   Guess what? Install dependencies:

   .. code-block:: shell

      yay -S python-aiohttp-security python-aiohttp-session python-cryptography python-aioauth-client

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
   Create service user:

   .. code-block:: shell

      sudo -u ahriman ahriman user-add --as-service -r write api

#. 
   Create end-user ``sudo -u ahriman ahriman user-add -r write my-first-user``. When it will ask for the password leave it blank.

#. Restart web service ``systemctl restart ahriman-web@x86_64``.

Backup and restore
------------------

The service provides several commands aim to do easy repository backup and restore. If you would like to move repository from the server ``server1.example.com`` to another ``server2.example.com`` you have to perform the following steps:

#. 
   On the source server ``server1.example.com`` run ``repo-backup`` command, e.g.:

   .. code-block:: shell

      sudo ahriman repo-backup /tmp/repo.tar.gz

   This command will pack all configuration files together with database file into the archive specified as command line argument (i.e. ``/tmp/repo.tar.gz``). In addition it will also archive ``cache`` directory (the one which contains local clones used by e.g. local packages) and ``.gnupg`` of the ``ahriman`` user.

#. 
   Copy created archive from source server ``server1.example.com`` to target ``server2.example.com``.

#. 
   Install ahriman as usual on the target server ``server2.example.com`` if you didn't yet.

#. 
   Extract archive e.g. by using subcommand:

   .. code-block:: shell

      sudo ahriman repo-restore /tmp/repo.tar.gz

   An additional argument ``-o``/``--output`` can be used to specify extraction root (``/`` by default).

#. 
   Rebuild repository:

   .. code-block:: shell

      sudo -u ahriman ahriman repo-rebuild --from-database

Other topics
------------

How does it differ from %another-manager%?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Short answer - I do not know.

`archrepo2 <https://github.com/lilydjwg/archrepo2>`_
""""""""""""""""""""""""""""""""""""""""""""""""""""

Don't know, haven't tried it. But it lacks of documentation at least.

* Web interface.
* No synchronization and reporting.
* ``archrepo2`` actively uses direct shell calls and ``yaourt`` components.
* It has constantly running process instead of timer process (it is not pro or con).

`repoctl <https://github.com/cassava/repoctl>`_
"""""""""""""""""""""""""""""""""""""""""""""""

* Web interface.
* No reporting.
* Local packages and patches support.
* Some actions are not fully automated (e.g. package update still requires manual intervention for the build itself). 
* ``repoctl`` has better AUR interaction features. With colors!
* ``repoctl`` has much easier configuration and even completion.
* ``repoctl`` is able to store old packages.
* Ability to host repository from same command vs external services (e.g. nginx) in ``ahriman``.

`repo-scripts <https://github.com/arcan1s/repo-scripts>`_
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Though originally I've created ahriman by trying to improve the project, it still lacks a lot of features:

* Web interface.
* Better reporting with template support.
* Synchronization features (there was only ``rsync`` based).
* Local packages and patches support.
* No dependency management.
* And so on.

``repo-scripts`` also have bad architecture and bad quality code and uses out-of-dated ``yaourt`` and ``package-query``.

`toolbox <https://github.com/chaotic-aur/toolbox>`_
"""""""""""""""""""""""""""""""""""""""""""""""""""

It is automation tools for ``repoctl`` mentioned above. Except for using shell it looks pretty cool and also offers some additional features like patches, remote synchronization (isn't it?) and reporting.

I would like to check service logs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the service writes logs to ``/dev/log`` which can be accessed by using ``journalctl`` command (logs are written to the journal of the user under which command is run).

You can also edit configuration and forward logs to ``stderr``, just change ``handlers`` value, e.g.:

.. code-block:: shell

   sed -i 's/handlers = syslog_handler/handlers = console_handler/g' /etc/ahriman.ini.d/logging.ini

You can even configure logging as you wish, but kindly refer to python ``logging`` module `configuration <https://docs.python.org/3/library/logging.config.html>`_. The application uses java concept to log messages, e.g. class ``Application`` imported from ``ahriman.application.application`` package will have logger called ``ahriman.application.application.Application``. In order to e.g. change logger name for whole application package it is possible to change values for ``ahriman.application`` package; thus editing ``ahriman`` logger configuration will change logging for whole application (unless there are overrides for another logger).

Html customization
^^^^^^^^^^^^^^^^^^

It is possible to customize html templates. In order to do so, create files somewhere (refer to Jinja2 documentation and the service source code for available parameters) and put ``template_path`` to configuration pointing to this directory.

I did not find my question
^^^^^^^^^^^^^^^^^^^^^^^^^^

`Create an issue <https://github.com/arcan1s/ahriman/issues>`_ with type **Question**.
