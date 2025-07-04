Configuration
=============

Some groups can be specified for each architecture and/or repository separately. E.g. if there are ``build`` and ``build:x86_64`` groups it will use an option from ``build:x86_64`` for the ``x86_64`` architecture and ``build`` for any other (architecture specific group has higher priority). In case if both groups are presented, architecture specific options will be merged into global ones overriding them. The order which will be used for option resolution is the following:

#. Repository and architecture specific, e.g. ``build:aur:x86_64``.
#. Repository specific, e.g. ``build:aur``.
#. Architecture specific, e.g. ``build:x86_64``.
#. Default section, e.g. ``build``.

There are two variable types which have been added to default ones, they are paths and lists. List values will be read in the same way as shell does:

* By default, it splits value by spaces excluding empty elements. 
* In case if quotation mark (``"`` or ``'``) will be found, any spaces inside will be ignored.
* In order to use quotation mark inside value it is required to put it to another quotation mark, e.g. ``wor"'"d "with quote"`` will be parsed as ``["wor'd", "with quote"]`` and vice versa.
* Unclosed quotation mark is not allowed and will raise an exception.

It is also possible to split list option between multiple declarations. To do so, append key name with ``[]`` (like PHP, sorry!), e.g.:

.. code-block:: ini

   [section]
   list[] = value1
   list[] = value2

will lead to ``${section:list}`` value to be set to ``value1 value2``. The values will be set in order of appearance, meaning that values which appear in different include files will be set in alphabetical order of file names. In order to reset list values, set option to empty string, e.g.:

.. code-block:: ini

   [section]
   list[] = value1
   list[] =
   list[] = value2
   list[] = value3

will set option ``${section:list}`` to ``value2 value3``. Alternatively, setting the original option (e.g. ``list`` in the example above) will also reset value, though the subsequent options with leading ``[]`` will append the previous value.

Path values, except for casting to ``pathlib.Path`` type, will be also expanded to absolute paths relative to the configuration path. E.g. if path is set to ``ahriman.ini.d/logging.ini`` and root configuration path is ``/etc/ahriman.ini``, the value will be expanded to ``/etc/ahriman.ini.d/logging.ini``. In order to disable path expand, use the full path, e.g. ``/etc/ahriman.ini.d/logging.ini``.

Configuration allows string interpolation from the same configuration file, e.g.:

.. code-block:: ini

   [section]
   key = ${another_key}
   another_key = value

will read value for the ``key`` option from ``another_key`` in the same section. In case if the cross-section reference is required, the ``${section:another_key}`` notation must be used. It also allows string interpolation from environment variables, e.g.:

.. code-block:: ini

   [section]
   key = $SECRET

will try to read value from ``SECRET`` environment variable. In case if the required environment variable wasn't found, it will keep original value (i.e. ``$SECRET`` in the example). Dollar sign can be set as ``$$``. All those interpolations will be applied in succession and - expected to be - recursively, e.g. the following configuration:

.. code-block:: ini

   [section1]
   key = ${section2:key}

   [section2]
   key = ${home}
   home = $HOME

will eventually lead ``key`` option in section ``section1`` to be set to the value of ``HOME`` environment variable (if available).

There is also additional subcommand which will allow to validate configuration and print found errors. In order to do so, run ``service-config-validate`` subcommand, e.g.:

.. code-block:: shell

   ahriman service-config-validate

It will check current settings on common errors and compare configuration with known schema.

``settings`` group
------------------

Base configuration settings.

* ``apply_migrations`` - perform database migrations on the application start, boolean, optional, default ``yes``. Useful if you are using git version. Note, however, that this option must be changed only if you know what to do and going to handle migrations manually.
* ``database`` - path to the application SQLite database, string, required.
* ``include`` - path to directory with configuration files overrides, string, optional. Files will be read in alphabetical order.
* ``keep_last_logs`` - amount of build logs to be kept for each package, integer, optional ,default ``0``. Logs will be cleared at the end of each process.
* ``logging`` - path to logging configuration, string, required. Check ``logging.ini`` for reference.

``alpm:*`` groups
-----------------

libalpm and AUR related configuration. Group name can refer to architecture, e.g. ``alpm:x86_64`` can be used for x86_64 architecture specific settings.

* ``database`` - path to pacman system database cache, string, required.
* ``mirror`` - package database mirror used by pacman for synchronization, string, required. This option supports standard pacman substitutions with ``$arch`` and ``$repo``. Note that the mentioned mirror should contain all repositories which are set by ``alpm.repositories`` option.
* ``repositories`` - list of pacman repositories, used for package search, space separated list of strings, required.
* ``root`` - root for alpm library, string, required. In the most cases it must point to the system root.
* ``sync_files_database`` - download files database from mirror, boolean, required.
* ``use_ahriman_cache`` - use local pacman package cache instead of system one, boolean, required. With this option enabled you might want to refresh database periodically (available as additional flag for some subcommands). If set to ``no``, databases must be synchronized manually.

``auth`` group
--------------

Base authorization settings. ``OAuth`` provider requires ``aioauth-client`` library to be installed.

* ``target`` - specifies authorization provider, string, optional, default ``disabled``. Allowed values are ``disabled``, ``configuration``, ``oauth``, ``pam``.
* ``allow_read_only`` - allow requesting status APIs without authorization, boolean, required.
* ``client_id`` - OAuth2 application client ID, string, required in case if ``oauth`` is used.
* ``client_secret`` - OAuth2 application client secret key, string, required in case if ``oauth`` is used.
* ``cookie_secret_key`` - secret key which will be used for cookies encryption, string, optional. It must be 32 bytes URL-safe base64-encoded and can be generated as following ``base64.urlsafe_b64encode(os.urandom(32)).decode("utf8")``. If not set, it will be generated automatically; note, however, that in this case, all sessions will be automatically invalidated during the service restart.
* ``full_access_group`` - name of the secondary group (e.g. ``wheel``) to be used as admin group in the service, string, required in case if ``pam`` is used.
* ``max_age`` - parameter which controls both cookie expiration and token expiration inside the service in seconds, integer, optional, default is 7 days.
* ``oauth_icon`` - OAuth2 login button icon, string, optional, default is ``google``. Must be valid `Bootstrap icon <https://icons.getbootstrap.com/>`__ name.
* ``oauth_provider`` - OAuth2 provider class name as is in ``aioauth-client`` (e.g. ``GoogleClient``, ``GithubClient`` etc), string, required in case if ``oauth`` is used.
* ``oauth_scopes`` - scopes list for OAuth2 provider, which will allow retrieving user email (which is used for checking user permissions), e.g. ``https://www.googleapis.com/auth/userinfo.email`` for ``GoogleClient`` or ``user:email`` for ``GithubClient``, space separated list of strings, required in case if ``oauth`` is used.
* ``permit_root_login`` - allow login as root user, boolean, optional, default ``no``.
* ``salt`` - additional password hash salt, string, optional.

Authorized users are stored inside internal database, if any of external providers (e.g. ``oauth``) are used, the password field for non-service users must be empty.

``build:*`` groups
------------------

Build related configuration. Group name can refer to architecture, e.g. ``build:x86_64`` can be used for x86_64 architecture specific settings.

* ``archbuild_flags`` - additional flags passed to ``archbuild`` command, space separated list of strings, optional.
* ``build_command`` - default build command, string, required.
* ``ignore_packages`` - list packages to ignore during a regular update (manual update will still work), space separated list of strings, optional.
* ``include_debug_packages`` - distribute debug packages, boolean, optional, default ``yes``.
* ``makepkg_flags`` - additional flags passed to ``makepkg`` command, space separated list of strings, optional.
* ``makechrootpkg_flags`` - additional flags passed to ``makechrootpkg`` command, space separated list of strings, optional.
* ``scan_paths`` - paths to be used for implicit dependencies scan, space separated list of strings, optional. If any of those paths is matched against the path, it will be added to the allowed list.
* ``triggers`` - list of ``ahriman.core.triggers.Trigger`` class implementation (e.g. ``ahriman.core.report.ReportTrigger ahriman.core.upload.UploadTrigger``) which will be loaded and run at the end of processing, space separated list of strings, optional. You can also specify triggers by their paths, e.g. ``/usr/lib/python3.10/site-packages/ahriman/core/report/report.py.ReportTrigger``. Triggers are run in the order of definition.
* ``triggers_known`` - optional list of ``ahriman.core.triggers.Trigger`` class implementations which are not run automatically and used only for trigger discovery and configuration validation.
* ``vcs_allowed_age`` - maximal age in seconds of the VCS packages before their version will be updated with its remote source, integer, optional, default is 7 days.
* ``workers`` - list of worker nodes addresses used for build process, space separated list of strings, optional. Each worker address must be valid and reachable URL, e.g. ``https://10.0.0.1:8080``. If none set, the build process will be run on the current node. There is also special trigger which loads this value based on the list of the discovered nodes.

``repository`` group
--------------------

Base repository settings.

* ``root`` - root path for application, string, required.

``sign:*`` groups
-----------------

Settings for signing packages or repository. Group name can refer to architecture, e.g. ``sign:x86_64`` can be used for x86_64 architecture specific settings.

* ``target`` - configuration flag to enable signing, space separated list of strings, required. Allowed values are ``package`` (sign each package separately), ``repository`` (sign repository database file).
* ``key`` - default PGP key, string, required. This key will also be used for database signing if enabled.

``status`` group
----------------

Reporting to web service related settings. In most cases there is fallback to web section settings.

* ``enabled`` - enable reporting to web service, boolean, optional, default ``yes`` for backward compatibility.
* ``address`` - remote web service address with protocol, string, optional. In case of websocket, the ``http+unix`` scheme and URL encoded address (e.g. ``%2Fvar%2Flib%2Fahriman`` for ``/var/lib/ahriman``) must be used, e.g. ``http+unix://%2Fvar%2Flib%2Fahriman%2Fsocket``. In case if none set, it will be guessed from ``web`` section.
* ``password`` - password to authorize in web service in order to update service status, string, required in case if authorization enabled.
* ``suppress_http_log_errors`` - suppress HTTP log errors, boolean, optional, default ``no``. If set to ``yes``, any HTTP log errors (e.g. if web server is not available, but HTTP logging is enabled) will be suppressed.
* ``timeout`` - HTTP request timeout in seconds, integer, optional, default is ``30``.
* ``username`` - username to authorize in web service in order to update service status, string, required in case if authorization enabled.

``web`` group
-------------

Web server settings. This feature requires ``aiohttp`` libraries to be installed.

* ``address`` - optional address in form ``proto://host:port`` (``port`` can be omitted in case of default ``proto`` ports), will be used instead of ``http://{host}:{port}`` in case if set, string, optional. This option is required in case if ``OAuth`` provider is used.
* ``autorefresh_intervals`` - enable page auto refresh options, space separated list of integers, optional. The first defined interval will be used as default. If no intervals set, the auto refresh buttons will be disabled. If first element of the list equals ``0``, auto refresh will be disabled by default.
* ``enable_archive_upload`` - allow to upload packages via HTTP (i.e. call of ``/api/v1/service/upload`` uri), boolean, optional, default ``no``.
* ``host`` - host to bind, string, optional.
* ``index_url`` - full URL of the repository index page, string, optional.
* ``max_body_size`` - max body size in bytes to be validated for archive upload, integer, optional. If not set, validation will be disabled.
* ``port`` - port to bind, integer, optional.
* ``service_only`` - disable status routes (including logs), boolean, optional, default ``no``.
* ``static_path`` - path to directory with static files, string, required.
* ``templates`` - path to templates directories, space separated list of paths, required.
* ``unix_socket`` - path to the listening unix socket, string, optional. If set, server will create the socket on the specified address which can (and will) be used by application. Note, that unlike usual host/port configuration, unix socket allows to perform requests without authorization.
* ``unix_socket_unsafe`` - set unsafe (o+w) permissions to unix socket, boolean, optional, default ``yes``. This option is enabled by default, because it is supposed that unix socket is created in safe environment (only web service is supposed to be used in unsafe), but it can be disabled by configuration.
* ``wait_timeout`` - wait timeout in seconds, maximum amount of time to be waited before lock will be free, integer, optional.

``keyring`` group
--------------------

Keyring package generator plugin.

* ``target`` - list of generator settings sections, space separated list of strings, required. It must point to valid section name.

Keyring generator plugin
^^^^^^^^^^^^^^^^^^^^^^^^

* ``type`` - type of the generator, string, optional, must be set to ``keyring-generator`` if exists.
* ``description`` - keyring package description, string, optional, default is ``repo PGP keyring``, where ``repo`` is the repository name.
* ``homepage`` - URL to homepage location if any, string, optional.
* ``license`` - list of licenses which are applied to this package, space separated list of strings, optional, default is ``Unlicense``.
* ``package`` - keyring package name, string, optional, default is ``repo-keyring``, where ``repo`` is the repository name.
* ``packagers`` - list of packagers keys, space separated list of strings, optional, if not set, the user keys from database will be used.
* ``revoked`` - list of revoked packagers keys, space separated list of strings, optional.
* ``trusted`` - list of master keys, space separated list of strings, optional, if not set, the ``key`` option from ``sign`` group will be used.

``mirrorlist`` group
--------------------

Mirrorlist package generator plugin.

* ``target`` - list of generator settings sections, space separated list of strings, required. It must point to valid section name.

Mirrorlist generator plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``type`` - type of the generator, string, optional, must be set to ``mirrorlist-generator`` if exists.
* ``description`` - mirrorlist package description, string, optional, default is ``repo mirror list for use by pacman``, where ``repo`` is the repository name.
* ``homepage`` - URL to homepage location if any, string, optional.
* ``license`` - list of licenses which are applied to this package, space separated list of strings, optional, default is ``Unlicense``.
* ``package`` - mirrorlist package name, string, optional, default is ``repo-mirrorlist``, where ``repo`` is the repository name.
* ``path`` - absolute path to generated mirrorlist file, string, optional, default is ``/etc/pacman.d/repo-mirrorlist``, where ``repo`` is the repository name.
* ``servers`` - list of repository mirrors, space separated list of strings, required.

``remote-pull`` group
---------------------

Remote git source synchronization settings. Unlike ``upload`` triggers those triggers are used for PKGBUILD synchronization - fetch from remote repository PKGBUILDs before updating process.

It supports authorization; to do so you'd need to prefix the URL with authorization part, e.g. ``https://key:token@github.com/arcan1s/ahriman.git``. It is highly recommended to use application tokens instead of your user authorization details. Alternatively, you can use any other option supported by git, e.g.:

* by SSH key: generate SSH key as ``ahriman`` user and put public part of it to the repository keys.
* by git credentials helper: consult with the `related man page <https://git-scm.com/docs/gitcredentials>`__.

Available options are:

* ``target`` - list of remote pull triggers to be used, space separated list of strings, optional, defaults to ``gitremote``. It must point to valid section (or to section with architecture), e.g. ``gitremote`` must point to either ``gitremote`` or ``gitremote:x86_64`` (the one with architecture has higher priority).

Remote pull trigger
^^^^^^^^^^^^^^^^^^^

* ``pull_url`` - URL of the remote repository from which PKGBUILDs can be pulled before build process, string, required.
* ``pull_branch`` - branch of the remote repository from which PKGBUILDs can be pulled before build process, string, optional, default is ``master``.

``remote-push`` group
---------------------

Remote git source synchronization settings. Same as remote pull triggers those triggers are used for PKGBUILD synchronization - push updated PKGBUILDs to the remote repository after build process.

It supports authorization; to do so you'd need to prefix the URL with authorization part, e.g. ``https://key:token@github.com/arcan1s/ahriman.git``. It is highly recommended to use application tokens instead of your user authorization details. Alternatively, you can use any other option supported by git, e.g.:

* by SSH key: generate SSH key as ``ahriman`` user and put public part of it to the repository keys.
* by git credentials helper: consult with the `related man page <https://git-scm.com/docs/gitcredentials>`__.

Available options are:

* ``target`` - list of remote push triggers to be used, space separated list of strings, optional, defaults to ``gitremote``. It must point to valid section (or to section with architecture), e.g. ``gitremote`` must point to either ``gitremote`` or ``gitremote:x86_64`` (the one with architecture has higher priority).

Remote push trigger
^^^^^^^^^^^^^^^^^^^

* ``commit_email`` - git commit email, string, optional, default is ``ahriman@localhost``.
* ``commit_user`` - git commit user, string, optional, default is ``ahriman``.
* ``push_url`` - URL of the remote repository to which PKGBUILDs should be pushed after build process, string, required.
* ``push_branch`` - branch of the remote repository to which PKGBUILDs should be pushed after build process, string, optional, default is ``master``.

``report`` group
----------------

Report generation settings.

* ``target`` - list of reports to be generated, space separated list of strings, required. It must point to valid section (or to section with architecture), e.g. ``somerandomname`` must point to existing section, ``email`` must point to either ``email`` or ``email:x86_64`` (the one with architecture has higher priority).

Type will be read from several sources:

* In case if ``type`` option set inside the section, it will be used.
* Otherwise, it will look for type from section name removing architecture name.
* And finally, it will use section name as type.

``console`` type
^^^^^^^^^^^^^^^^

Section name must be either ``console`` (plus optional architecture name, e.g. ``console:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``console`` if exists.
* ``use_utf`` - use utf8 symbols in output if set and ascii otherwise, boolean, optional, default ``yes``.

``email`` type
^^^^^^^^^^^^^^

Section name must be either ``email`` (plus optional architecture name, e.g. ``email:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``email`` if exists.
* ``homepage`` - link to homepage, string, optional.
* ``host`` - SMTP host for sending emails, string, required.
* ``link_path`` - prefix for HTML links, string, required.
* ``no_empty_report`` - skip report generation for empty packages list, boolean, optional, default ``yes``.
* ``password`` - SMTP password to authenticate, string, optional.
* ``port`` - SMTP port for sending emails, integer, required.
* ``receivers`` - SMTP receiver addresses, space separated list of strings, required.
* ``rss_url`` - link to RSS feed, string, optional.
* ``sender`` - SMTP sender address, string, required.
* ``ssl`` - SSL mode for SMTP connection, one of ``ssl``, ``starttls``, ``disabled``, optional, default ``disabled``.
* ``template`` - Jinja2 template name, string, required.
* ``template_full`` - Jinja2 template name for full package description index, string, optional.
* ``templates`` - path to templates directories, space separated list of paths, required.
* ``user`` - SMTP user to authenticate, string, optional.

``html`` type
^^^^^^^^^^^^^

Section name must be either ``html`` (plus optional architecture name, e.g. ``html:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``html`` if exists.
* ``homepage`` - link to homepage, string, optional.
* ``link_path`` - prefix for HTML links, string, required.
* ``path`` - path to HTML report file, string, required.
* ``rss_url`` - link to RSS feed, string, optional.
* ``template`` - Jinja2 template name, string, required.
* ``templates`` - path to templates directories, space separated list of paths, required.

``remote-call`` type
^^^^^^^^^^^^^^^^^^^^

Section name must be either ``remote-call`` (plus optional architecture name, e.g. ``remote-call:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``remote-call`` if exists.
* ``aur`` - check for AUR packages updates, boolean, optional, default ``no``.
* ``local`` - check for local packages updates, boolean, optional, default ``no``.
* ``manual`` - update manually built packages, boolean, optional, default ``no``.
* ``wait_timeout`` - maximum amount of time in seconds to be waited before remote process will be terminated, integer, optional, default ``-1``.

``rss`` type
^^^^^^^^^^^^

Section name must be either ``rss`` (plus optional architecture name, e.g. ``rss:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``rss`` if exists.
* ``homepage`` - link to homepage, string, optional.
* ``link_path`` - prefix for HTML links, string, required.
* ``max_entries`` - maximal amount of entries to be included to the report, negative means no limit, integer, optional, default ``-1``.
* ``path`` - path to generated RSS file, string, required.
* ``rss_url`` - link to RSS feed, string, optional.
* ``template`` - Jinja2 template name, string, required.
* ``templates`` - path to templates directories, space separated list of paths, required.

``telegram`` type
^^^^^^^^^^^^^^^^^

Section name must be either ``telegram`` (plus optional architecture name, e.g. ``telegram:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``telegram`` if exists.
* ``api_key`` - telegram bot API key, string, required. Please refer FAQ about how to create chat and bot
* ``chat_id`` - telegram chat id, either string with ``@`` or integer value, required.
* ``homepage`` - link to homepage, string, optional.
* ``link_path`` - prefix for HTML links, string, required.
* ``rss_url`` - link to RSS feed, string, optional.
* ``template`` - Jinja2 template name, string, required.
* ``template_type`` - ``parse_mode`` to be passed to telegram API, one of ``MarkdownV2``, ``HTML``, ``Markdown``, string, optional, default ``HTML``.
* ``templates`` - path to templates directories, space separated list of paths, required.
* ``timeout`` - HTTP request timeout in seconds, integer, optional, default is ``30``.

``upload`` group
----------------

Remote synchronization settings.

* ``target`` - list of synchronizations to be used, space separated list of strings, required. It must point to valid section (or to section with architecture), e.g. ``somerandomname`` must point to existing section, ``github`` must point to one of ``github`` of ``github:x86_64`` (with architecture it has higher priority).

Type will be read from several sources:

* In case if ``type`` option set inside the section, it will be used.
* Otherwise, it will look for type from section name removing architecture name.
* And finally, it will use section name as type.

``github`` type
^^^^^^^^^^^^^^^

This feature requires GitHub key creation (see below). Section name must be either ``github`` (plus optional architecture name, e.g. ``github:x86_64``) or random name with ``type`` set.

* ``type`` - type of the upload, string, optional, must be set to ``github`` if exists.
* ``owner`` - GitHub repository owner, string, required.
* ``password`` - created GitHub API key. In order to create it do the following:

  #. Go to `settings page <https://github.com/settings/profile>`__.
  #. Switch to `developers settings <https://github.com/settings/apps>`__.
  #. Switch to `personal access tokens <https://github.com/settings/tokens>`__.
  #. Generate new token. Required scope is ``public_repo`` (or ``repo`` for private repository support).

* ``repository`` - GitHub repository name, string, required. Repository must be created before any action and must have active branch (e.g. with readme).
* ``timeout`` - HTTP request timeout in seconds, integer, optional, default is ``30``.
* ``use_full_release_name`` - if set to ``yes``, the release will contain both repository name and architecture, and only architecture otherwise, boolean, optional, default ``no`` (legacy behavior).
* ``username`` - GitHub authorization user, string, required. Basically the same as ``owner``.

``remote-service`` type
^^^^^^^^^^^^^^^^^^^^^^^

Section name must be either ``remote-service`` (plus optional architecture name, e.g. ``remote-service:x86_64``) or random name with ``type`` set.

* ``type`` - type of the report, string, optional, must be set to ``remote-service`` if exists.
* ``timeout`` - HTTP request timeout in seconds, integer, optional, default is ``30``.

``rsync`` type
^^^^^^^^^^^^^^

Requires ``rsync`` package to be installed. Do not forget to configure ssh for user ``ahriman``. Section name must be either ``rsync`` (plus optional architecture name, e.g. ``rsync:x86_64``) or random name with ``type`` set.

* ``type`` - type of the upload, string, optional, must be set to ``rsync`` if exists.
* ``command`` - rsync command to run, space separated list of string, required.
* ``remote`` - remote server to rsync (e.g. ``ahriman@10.0.0.1:/srv/repo``), string, required.

``s3`` type
^^^^^^^^^^^

Requires ``boto3`` library to be installed. Section name must be either ``s3`` (plus optional architecture name, e.g. ``s3:x86_64``) or random name with ``type`` set.

* ``type`` - type of the upload, string, optional, must be set to ``s3`` if exists.
* ``access_key`` - AWS access key ID, string, required.
* ``bucket`` - bucket name (e.g. ``bucket``), string, required.
* ``chunk_size`` - chunk size for calculating entity tags, integer, optional, default 8 * 1024 * 1024.
* ``object_path`` - path prefix for stored objects, string, optional. If none set, the prefix as in repository tree will be used.
* ``region`` - bucket region (e.g. ``eu-central-1``), string, required.
* ``secret_key`` - AWS secret access key, string, required.

``worker`` group
----------------

This section controls settings for ``ahriman.core.distributed.WorkerTrigger`` plugin.

* ``address`` - address of the instance, string, required. Must be reachable for the master instance.
* ``identifier`` - unique identifier of the instance, string, optional.
* ``time_to_live`` - amount of time which remote worker will be considered alive in seconds, integer, optional, default is ``60``. The ping interval will be set automatically equal this value divided by 4.
