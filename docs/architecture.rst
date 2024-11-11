Architecture
============

Package structure
-----------------

Packages have strict rules of importing:

* ``ahriman.application`` package must not be used outside of this package.
* ``ahriman.core`` and ``ahriman.models`` packages don't have any import restriction. Actually we would like to totally restrict importing of ``core`` package from ``models``, but it is impossible at the moment.
* ``ahriman.web`` package is allowed to be imported from ``ahriman.application`` (web handler only, only ``ahriman.web.web`` methods).
* The idea remains the same for all imports, if an package requires some specific dependencies, it must be imported locally to keep dependencies optional.

Full dependency diagram:

.. graphviz:: _static/architecture.dot
   :alt: architecture

``ahriman.application`` package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This package contains application (aka executable) related classes and everything for it. It also contains package called ``ahriman.application.handlers`` in which all available subcommands are described as separated classes derived from the base ``ahriman.application.handlers.handler.Handler`` class. Those classes are being loaded dynamically through the lookup of the ``ahriman.application.handlers`` package.

``ahriman.application.application.Application`` (god class) is used for any interaction from parsers with repository. It is divided into multiple traits by functions (package related and repository related) in the same package.

``ahriman.application.application.workers`` package contains specific wrappers for local and remote build processes.

``ahriman.application.ahriman`` contains only command line parses and executes specified ``Handler`` on success, ``ahriman.application.lock.Lock`` is additional class which provides file-based lock and also performs some common checks.

``ahriman.core`` package
^^^^^^^^^^^^^^^^^^^^^^^^

This package contains everything required for the most of application actions and it is separated into several packages:

* ``ahriman.core.alpm`` package controls pacman related functions. It provides wrappers for ``pyalpm`` library and safe calls for repository tools (``repo-add`` and ``repo-remove``). Also this package contains ``ahriman.core.alpm.remote`` package which provides wrapper for remote sources (e.g. AUR RPC and official repositories RPC) and some other helpers.
* ``ahriman.core.auth`` package provides classes for authorization methods used by web mostly. Base class is ``ahriman.core.auth.Auth`` which must be instantiated by ``load`` method. This package is only required by the ``ahriman.web`` package.
* ``ahriman.core.build_tools`` is a package which provides wrapper for ``devtools`` commands.
* ``ahriman.core.configuration`` contains extensions for standard ``configparser`` module and some validation related classes.
* ``ahriman.core.database`` is everything for database, including data and schema migrations.
* ``ahriman.core.distributed`` package with triggers and helpers for distributed build system.
* ``ahriman.core.formatters`` package provides ``Printer`` sub-classes for printing data (e.g. package properties) to stdout which are used by some handlers.
* ``ahriman.core.gitremote`` is a package with remote PKGBUILD triggers. Should not be called directly.
* ``ahriman.core.http`` package provides HTTP clients which can be used later by other classes.
* ``ahriman.core.log`` is a log utils package. It includes logger loader class, custom HTTP based logger and some wrappers.
* ``ahriman.core.report`` is a package with reporting triggers. Should not be called directly.
* ``ahriman.core.repository`` contains several traits and base repository (``ahriman.core.repository.Repository`` class) implementation.
* ``ahriman.core.sign`` package provides sign feature (only gpg calls are available).
* ``ahriman.core.status`` contains helpers and watcher class which are required for web application. Reporter must be initialized by using ``ahriman.core.status.client.Client.load`` method.
* ``ahriman.core.support`` provides plugins for support packages (mirrorlist and keyring) generation.
* ``ahriman.core.triggers`` package contains base trigger classes. Classes from this package must be imported in order to implement user extensions. In fact, ``ahriman.core.report``, ``ahriman.core.upload`` and other built-in triggers use this package.
* ``ahriman.core.upload`` package provides sync feature, should not be called directly.

This package also provides some generic functions and classes which may be used by other packages:

* ``ahriman.core.exceptions`` provides custom exceptions.
* ``ahriman.core.module_loader`` provides ``implementations`` method which can be used for dynamic classes load. In particular, this method is used for web views and application handlers loading.
* ``ahriman.core.spawn.Spawn`` is a tool which can spawn another ``ahriman`` process. This feature is used by web application.
* ``ahriman.core.tree`` is a dependency tree implementation.
* ``ahriman.core.types`` are an additional global types for mypy checks.
* ``ahriman.core.utils`` contains some useful functions which are not the part of any other class.

``ahriman.models`` package
^^^^^^^^^^^^^^^^^^^^^^^^^^

It provides models for any other part of application. Unlike ``ahriman.core`` package classes from here provide only conversion methods (e.g. create class from another or convert to). It is mostly presented by case classes and enumerations.

``ahriman.web`` package
^^^^^^^^^^^^^^^^^^^^^^^

Web application. It is important that this package is isolated from any other to allow it to be optional feature (i.e. dependencies which are required by the package are optional).

* ``ahriman.web.middlewares`` provides middlewares for request handlers.
* ``ahriman.web.schemas`` provides schemas (actually copy paste from dataclasses) used by swagger documentation.
* ``ahriman.web.views`` contains web views derived from aiohttp view class. Those classes are loaded dynamically through the filesystem lookup.
* ``ahriman.web.apispec`` provides generators for swagger documentation.
* ``ahriman.web.cors`` contains helpers for cross origin resource sharing middlewares.
* ``ahriman.web.routes`` creates routes for web application.
* ``ahriman.web.web`` provides main web application functions (e.g. start, initialization).

Application run
---------------

#. Parse command line arguments, find subcommand and related handler which is set by the parser.
#. Call ``Handler.execute`` method.
#. Define list of architectures to run. In case if there is more than one architecture specified run several subprocesses or continue in current process otherwise. Class attribute ``ALLOW_MULTI_ARCHITECTURE_RUN`` controls whether the application can be run in multiple processes or not - this feature is required for some handlers (e.g. ``Config``, which utilizes stdout to print messages).
#. In each child process call lock functions.
#. After success checks pass control to ``Handler.run`` method defined by specific handler class.
#. Return result (success or failure) of each subprocess and exit from application.
#. Some handlers may override their status and throw ``ExitCode`` exception. This exception is just silently suppressed and changes application exit code to ``1``.

In the most cases handlers spawn god class ``ahriman.application.application.Application`` class and call required methods.

The application is designed to run from ``systemd`` services and provides parametrized by repository identifier timer and service file for that.

Subcommand design
^^^^^^^^^^^^^^^^^

All subcommands are divided into several groups depending on the role they are doing:

* ``aur`` (``aur-search``) group is for AUR operations.
* ``help`` (e.g. ``help``) are system commands.
* ``package`` subcommands (e.g. ``package-add``) allow to perform single package actions.
* ``patch`` subcommands (e.g. ``patch-list``) are the special case of ``package`` subcommands introduced in order to control patches for packages.
* ``repo`` subcommands (e.g. ``repo-check``) usually perform actions on whole repository.
* ``service`` subcommands (e.g. ``service-setup``) perform actions which are related to whole service managing: create repository, show configuration.
* ``user`` subcommands (``user-add``) are intended for user management.
* ``web`` subcommands are related to web service management.

For historical reasons and in order to keep backward compatibility some subcommands have aliases to their shorter forms or even other groups, but the application doesn't guarantee that they will remain unchanged.

Filesystem tree
---------------

The application supports two types of trees, one is for the legacy configuration (when there were no explicit repository name configuration available) and another one is the new-style tree. This document describes only new-style tree in order to avoid deprecated structures.

Having default root as ``/var/lib/ahriman`` (differs from container though), the directory structure is the following:

.. code-block::

   /var/lib/ahriman/
   ├── ahriman.db
   ├── cache
   ├── chroot
   │   └── aur
   ├── packages
   │   └── aur
   │       └── x86_64
   ├── pacman
   │   └── aur
   │       └── x86_64
   │           ├── local
   │           │   └── ALPM_DB_VERSION
   │           └── sync
   │               ├── core.db
   │               ├── extra.db
   │               └── multilib.db
   │
   └── repository
       └── aur
           └── x86_64
               ├── aur.db -> aur.db.tar.gz
               ├── aur.db.tar.gz
               ├── aur.files -> aur.files.tar.gz
               └── aur.files.tar.gz

There are multiple subdirectories, some of them are commons for any repository, but some of them are not.

* ``cache`` is a directory with locally stored PKGBUILD's and VCS packages. It is common for all repositories and architectures.
* ``chroot/{repository}`` is a chroot directory for ``devtools``. It is specific for each repository, but shared for different architectures inside (the ``devtools`` handles architectures automatically).
* ``packages/{repository}/{architecture}`` is a directory with prebuilt packages. When a package is built, first it will be uploaded to this directory and later will be handled by update process. It is architecture and repository specific.
* ``pacman/{repository}/{architecture}`` is the repository and architecture specific caches for pacman's databases.
* ``repository/{repository}/{architecture}`` is a repository packages directory.

Normally you should avoid direct interaction with the application tree. For tree migration process refer to the :doc:`migration notes <migrations/index>`.

Database
--------

The service uses SQLite database in order to store some internal info.

Database instance
^^^^^^^^^^^^^^^^^

All methods related to the specific part of database (basically operations per table) are split into different traits located inside ``ahriman.core.database.operations`` package. The base trait ``ahriman.core.database.operations.Operations`` also provides generic methods for database access (e.g. row converters and transactional support).

The ``ahriman.core.database.SQLite`` class itself derives from all of these traits and implements methods for initialization, including migrations.

Schema and data migrations
^^^^^^^^^^^^^^^^^^^^^^^^^^

The schema migrations are applied according to current ``pragma user_info`` values, located at ``ahriman.core.database.migrations`` package and named as ``m000_migration_name.py`` (the preceding ``m`` is required in order to import migration content for tests). Additional class ``ahriman.core.database.migrations.Migrations`` reads all migrations automatically and applies them in alphabetical order.

These migrations can also contain data migrations. Though the recommended way is to migrate data directly from SQL queries, sometimes it is required to have external data (like packages list) in order to set correct data. To do so, special method ``migrate_data`` is used.

Type conversions
^^^^^^^^^^^^^^^^

By default, it parses rows into python dictionary. In addition, the following pseudo-types are supported:

* ``dict[str, Any]`` and ``list[Any]`` - for storing JSON data structures in database (technically there is no restriction on types for dictionary keys and values, but it is recommended to use only string keys). The type is stored as ``json`` data type and ``json.loads`` and ``json.dumps`` methods are used in order to read and write from/to database respectively.

Basic flows
-----------

By default package build operations are performed with ``PACKAGER`` which is specified in ``makepkg.conf``, however, it is possible to override this variable from command line; in this case service performs lookup in the following way:

* If packager is not set, it reads environment variables (e.g. ``DOAS_USER``, ``SUDO_USER`` and ``USER``), otherwise it uses value from command line.
* It checks users for the specified username and tries to extract packager variable from it.
* If packager value has been found, it will be passed as ``PACKAGER`` system variable (additional sudo configuration to pass environment variables might be required).

Add new packages or rebuild existing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The idea is to add package to a build queue from which it will be handled automatically during the next update run. Different variants are supported:

* If supplied argument is file, then application moves the file to the directory with the built packages. Same rule is applied for directory, but in this case it copies every package-like file from the specified directory.
* If supplied argument is directory and there is ``PKGBUILD`` file there, it will be treated as local package. In this case it will queue this package to build and copy source files (``PKGBUILD`` and ``.SRCINFO``) to caches.
* If supplied argument looks like URL (i.e. it has scheme, which is neither ``data`` nor ``file``, e.g. ``http://``), it tries to download the package from the specified remote source.
* If supplied argument is not file then application tries to lookup for the specified name in AUR and clones it into the temporary directory, from which it will be added into the build queue. This scenario can also handle package dependencies which are missing in repositories.

This logic can be overwritten by specifying the ``source`` parameter, which is partially useful if you would like to add package from AUR, but there is local directory cloned from AUR. Also the official repositories calls are hidden behind explicit source definition.

Rebuild packages
^^^^^^^^^^^^^^^^

Same as add function for every package in repository. Optional filters by reverse dependency or build status can be supplied.

Remove packages
^^^^^^^^^^^^^^^

This flow removes package from filesystem, updates repository database and also runs synchronization and reporting methods.

Check outdated packages
^^^^^^^^^^^^^^^^^^^^^^^

There are few ways for packages to be marked as out-of-date and hence requiring rebuild. Those are following:

#. User requested update of the package. It can be caused by calling ``package-add`` subcommand (or ``package-update`` with arguments).
#. The most common way for packages to be marked as out-of-dated is that the version in AUR (or the official repositories) is newer than in the repository.
#. In addition to the above, if package is named as VCS (e.g. has suffix ``-git``) and the last update was more than specified threshold ago, the service will also try to fetch sources and check if the revision is newer than the built one.
#. In addition, there is ability to check if the dependencies of the package have been updated (e.g. if linked library has been renamed or the modules directory - e.g. in case of python and ruby packages - has been changed). And if so, the package will be marked as out-of-dated as well.

Update packages
^^^^^^^^^^^^^^^

This feature is divided into the following stages: check AUR for updates and run rebuild for required packages. The package update flow is the following:

#. Process every built package first. Those packages are usually added manually.
#. Run sync and report methods.
#. Generate dependency tree for packages to be built.
#. For each level of tree it does:

   #. Download package data from AUR.
   #. Bump ``pkgrel`` if there is duplicate version in the local repository (see explanation below).
   #. Build every package in clean chroot.
   #. Sign packages if required.
   #. Add packages to database and sign database if required.
   #. Process triggers.

After any step any package data is being removed.

In case if there are configured workers, the build process itself will be delegated to the remote instances. Packages will be partitioned to the chunks according to the amount of configured workers.

Distributed builds
^^^^^^^^^^^^^^^^^^

This feature consists of two parts:

* Upload built packages to the node.
* Delegate packages building to separated nodes.

The upload process is performed via special API endpoint, which is disabled by default, and is performed in several steps:

#. Upload package to temporary file.
#. Copy content from temporary file to the built package directory with dot (``.``) prefix.
#. Rename copied file, removing preceding dot.

After success upload, the update process must be called as usual in order to copy built packages to the main repository tree.

On the other side, the delegation uses upload feature, but in addition it also calls external services in order to trigger build process. The packages are separated into the chunks based on the amount of the configured workers and their dependencies.

pkgrel bump rules
^^^^^^^^^^^^^^^^^

The application is able to automatically bump package release (``pkgrel`` variable) during the build process if there is duplicated version in the repository. The version will be incremented as following:

#. Get version of the remote package.
#. Get version of the local package if available.
#. If the local version is not set, proceed with the remote one.
#. If the local version is set and the remote version is newer than local one, proceed with remote.
#. Extract ``pkgrel`` value.
#. If it has ``major.minor`` notation (e.g. ``1.1``), then increment last part by 1, e.g. ``1.1 -> 1.2``, ``1.0.1 -> 1.0.2``.
#. If ``pkgrel`` is a number (e.g. ``1``), then append 1 to the end of the string, e.g. ``1 -> 1.1``.

Implicit dependencies resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In addition to the depends/optional/make/check depends lists the server also handles implicit dependencies. After success build, the application traverse through the build tree and finds:

* Libraries to which the binaries (ELF-files) are linked. To do so, the ``NEEDED`` section of the ELF-files is read.
* Directories which contains files of the package, but do not belong to this package. This case covers, for example, python and ruby submodules.

Having the initial dependencies tree, the application is looking for packages which contains those (both files and directories) paths and creates the initial packages list. After that, the packages list is reduced in the following way:

* From any leaf exclude the package itself and possible debug packages.
* If the entry (i.e. file or directory) belongs to the package which is in base group, it will be removed.
* If there is a package which depends on the another package which provide the same entry, the package will be removed.
* After that, if there is a package which *optionally* depends on the another package in the remaining list, the package will be removed.
* And finally, if there is any path, which is the child of the entry, and it contains the same package, the package from the smaller entry will be removed.

Those paths are also filtered by regular expressions set in the configuration.

All those implicit dependencies are stored in the database and extracted on each check. In case if any of the repository packages doesn't contain any entry anymore (e.g. so version has been changed or modules directory has been changed), the dependent package will be marked as out-of-dated.

Core functions reference
------------------------

Configuration
^^^^^^^^^^^^^

``ahriman.core.configuration.Configuration`` class provides some additional methods (e.g. ``getpath`` and ``getlist``) and also combines multiple files into single configuration dictionary using repository identifier overrides. It is the recommended way to deal with settings.

Enumerations
^^^^^^^^^^^^

All enumerations are derived from ``enum.StrEnum``. Integer enumerations in general are not allowed, because most of operations require conversions from string variable. Derivation from string based enumeration is required to make json conversions implicitly (e.g. during calling ``json.dumps`` methods).

In addition, some enumerations provide ``from_option`` class methods in order to allow some flexibility while reading configuration options.

Utils
^^^^^

For every external command run (which is actually not recommended if possible) custom wrapper for ``subprocess`` is used. Additional functions ``ahriman.core.auth.helpers`` provide safe calls for ``aiohttp_security`` methods and are required to make this dependency optional.

Context variables
^^^^^^^^^^^^^^^^^

Package provides implicit global variables which can be accessed from ``ahriman.core`` package as ``context`` variable, wrapped by ``contextvars.ContextVar`` class. The value of the variable is defaulting to private ``_Context`` class which is defined in the same module. The default values - such as ``database`` and ``sign`` - are being set on the service initialization.

The ``_Context`` class itself mimics default collection interface (as is ``Mapping``) and can be modified by ``_Context.set`` method. The stored variables can be achieved by ``_Context.get`` method, which is unlike default ``Mapping`` interface also performs type and presence checks.

In order to provide statically typed interface, the ``ahriman.models.context_key.ContextKey`` class is used for both ``_Content.get`` and ``_Content.set`` methods; the context instance itself, however, does not store information about types.

Submodules
^^^^^^^^^^

Some packages provide different behaviour depending on configuration settings. In these cases inheritance is used and recommended way to deal with them is to call class method ``load`` from base classes.

Authorization
^^^^^^^^^^^^^

The package provides several authorization methods: disabled, based on configuration, PAM and OAuth2.

Disabled (default) authorization provider just allows everything for everyone and does not have any specific configuration (it uses some default configuration parameters though). It also provides generic interface for derived classes.

Mapping (aka configuration) provider uses hashed passwords with optional salt from the database in order to authenticate users. This provider also enables user permission checking (read/write) (authorization). Thus, it defines the following methods:

* ``check_credentials`` - user password validation (authentication).
* ``verify_access`` - user permission validation (authorization).

Passwords must be stored in database as ``hash(password + salt)``, where ``password`` is user defined password (taken from user input), ``salt`` is random string (any length) defined globally in configuration and ``hash`` is a secure hash function. Thus, the following configuration

.. code-block::

   "username","password","access"
   "username","$6$rounds=656000$mWBiecMPrHAL1VgX$oU4Y5HH8HzlvMaxwkNEJjK13ozElyU1wAHBoO/WW5dAaE4YEfnB0X3FxbynKMl4FBdC3Ovap0jINz4LPkNADg0","read"

means that there is user ``username`` with ``read`` access and password ``password`` hashed by ``sha512`` with salt ``salt``.

OAuth provider uses library definitions (``aioauth-client``) in order *authenticate* users. It still requires user permission to be set in database, thus it inherits mapping provider without any changes. Whereas we could override ``check_credentials`` (authentication method) by something custom, OAuth flow is a bit more complex than just forward request, thus we have to implement the flow in login form.

OAuth's implementation also allows authenticating users via username + password (in the same way as mapping does) though it is not recommended for end-users and password must be left blank. In particular this feature can be used by service reporting (aka robots).

In addition, web service checks the source socket used. In case if it belongs to ``socket.AF_UNIX`` family, it will skip any further checks considering the request to be performed in safe environment (e.g. on the same physical machine). This feature, in particular is being used by the reporter instances in case if socket address is set in configuration. Note, however, that this behaviour can be disabled by configuration.

In order to configure users there are special subcommands.

Triggers
^^^^^^^^

Triggers are extensions which can be used in order to perform any actions on application start, after the update process and, finally, before the application exit.

The main idea is to load classes by their full path (e.g. ``ahriman.core.upload.UploadTrigger``) by using ``importlib``: get the last part of the import and treat it as class name, join remain part by ``.`` and interpret as module path, import module and extract attribute from it.

The loaded triggers will be called with ``ahriman.models.result.Result`` and ``list[Packages]`` arguments, which describes the process result and current repository packages respectively. Any exception raised will be suppressed and will generate an exception message in logs.

In addition triggers can implement ``on_start`` and ``on_stop`` actions which will be called on the application start and right before the application exit respectively. The ``on_start`` action is usually being called from handlers directly in order to make sure that no trigger will be run when it is not required (e.g. on user management). As soon as ``on_start`` action is called, the additional flag will be set; ``ahriman.core.triggers.TriggerLoader`` class implements ``__del__`` method in which, if the flag is set, the ``on_stop`` actions will be called.

For more details how to deal with the triggers, refer to :doc:`documentation <triggers>` and modules descriptions.

Remote synchronization
^^^^^^^^^^^^^^^^^^^^^^

There are several supported synchronization providers, currently they are ``rsync``, ``s3``, ``github``.

``rsync`` provider does not have any specific logic except for running external rsync application with configured arguments. The service does not handle SSH configuration, thus it has to be configured before running application manually.

``s3`` provider uses ``boto3`` package and implements sync feature. The files are stored in architecture specific directory (e.g. if bucket is ``repository``, packages will be stored in ``repository/aur/x86_64`` for the ``aur`` repository and ``x86_64`` architecture), bucket must be created before any action and API key must have permissions to write to the bucket. No external configuration required. In order to upload only changed files the service compares calculated hashes with the Amazon ETags, the implementation used is described `here <https://teppen.io/2018/10/23/aws_s3_verify_etags/>`__.

``github`` provider authenticates through basic auth, API key with repository write permissions is required. There will be created a release with the name of the architecture in case if it does not exist; files will be uploaded to the release assets. It also stores array of files and their MD5 checksums in release body in order to upload only changed ones. According to the GitHub API in case if there is already uploaded asset with the same name (e.g. database files), asset will be removed first.

PKGBUILD parsing
^^^^^^^^^^^^^^^^

The application provides a house-made shell parser ``ahriman.core.alpm.pkgbuild_parser.PkgbuildParser`` to process PKGBUILDs and extract package data from them. It relies on the ``shlex.shlex`` parser with some configuration tweaks and adds some token post-processing.

#. During the parser process, firstly, it extract next token from the source file (basically, the word) and tries to match it to the variable assignment. If so, then just processes accordingly.
#. If it is not an assignment, the parser checks if the token was quoted.
#. If it wasn't quoted then the parser tries to match the array starts (two consecutive tokens like ``array=`` and ``(``) or it is function (``function``, ``()`` and ``{``).
#. The arrays are processed until the next closing bracket ``)``. After extraction, the parser tries to expand an array according to bash rules (``prefix{first,second}suffix`` constructions).
#. The functions are just read until the closing bracket ``}`` and then reread whole text from the input string without a tokenization.

All extracted fields are packed as ``ahriman.models.pkgbuild_patch.PkgbuildPatch`` and then can be used as ``ahriman.models.pkgbuild.Pkgbuild`` instance.

The PKGBUILD class also provides some additional functions on top of that:

* Ability to extract fields defined inside ``package*()`` functions, which are in particular used for the multi-packages.
* Shell substitution, which supports constructions ``$var`` (including ``${var}``), ``${var#(#)pattern}``, ``${var%(%)pattern}`` and ``${var/(/)pattern/replacement}`` (including ``#pattern`` and ``%pattern``).

Additional features
^^^^^^^^^^^^^^^^^^^

Some features require optional dependencies to be installed:

* ``gnupg`` application for package and repository sign feature.
* ``rsync`` application for rsync based repository sync.
* ``boto3`` python package for ``S3`` sync.
* ``Jinja2`` python package for HTML report generation (it is also used by web application).

Web application
---------------

Web application requires the following python packages to be installed:

* Core part requires ``aiohttp`` (application itself), ``aiohttp_jinja2`` and ``Jinja2`` (HTML generation from templates).
* Additional web features also require ``aiohttp-apispec`` (autogenerated documentation), ``aiohttp_cors`` (CORS support, required by documentation).
* In addition, authorization feature requires ``aiohttp_security``, ``aiohttp_session`` and ``cryptography``.
* In addition to base authorization dependencies, OAuth2 also requires ``aioauth-client`` library.
* In addition if you would like to disable authorization for local access (recommended way in order to run the application itself with reporting support), the ``requests-unixsocket2`` library is required.

Middlewares
^^^^^^^^^^^

Service provides some custom middlewares, e.g. logging every exception (except for user ones) and user authorization.

HEAD and OPTIONS requests
^^^^^^^^^^^^^^^^^^^^^^^^^

``HEAD`` request is automatically generated by ``ahriman.web.views.base.BaseView`` class. It just calls ``GET`` method, removes any data from body and returns the result. In case if no ``GET`` method available for this view, the ``aiohttp.web.HTTPMethodNotAllowed`` exception will be raised.

On the other side, ``OPTIONS`` method is implemented in the ``ahriman.web.middlewares.exception_handler.exception_handler`` middleware. In case if ``aiohttp.web.HTTPMethodNotAllowed`` exception is raised and original method was ``OPTIONS``, the middleware handles it, converts to valid request and returns response to user.

Web views
^^^^^^^^^

All web views are defined in separated package and derived from ``ahriman.web.views.base.Base`` class which provides typed interfaces for web application. 

REST API supports only JSON data.

Different APIs are separated into different packages:

* ``ahriman.web.views.api`` not a real API, but some views which provide OpenAPI support.
* ``ahriman.web.views.*.auditlog`` provides event log API.
* ``ahriman.web.views.*.distributed`` is an API for builders interaction for multi-node setup.
* ``ahriman.web.views.*.packages`` contains views which provide information about existing packages.
* ``ahriman.web.views.*.service`` provides views for application controls.
* ``ahriman.web.views.*.status`` package provides REST API for application reporting.
* ``ahriman.web.views.*.user`` package provides login and logout methods which can be called without authorization.

The views are also divided by supporting API versions (e.g. ``v1``, ``v2``).

Templating
^^^^^^^^^^

Package provides base jinja templates which can be overridden by settings. Vanilla templates actively use bootstrap library.

Requests and scopes
^^^^^^^^^^^^^^^^^^^

Service provides optional authorization which can be turned on in settings. In order to control user access there are two levels of authorization - read-only (only GET-like requests) and write (anything), settings for which are provided by each web view directly.

If this feature is configured any request will be prohibited without authentication. In addition, configuration flag ``auth.allow_read_only`` can be used in order to allow read-only operations - reading index page and packages - without authorization.

For authenticated users it uses encrypted session cookies to store tokens; encryption key is read from configuration or generated at the start of the application if not set. It also stores expiration time of the session inside.

External calls
^^^^^^^^^^^^^^

Web application provides external calls to control main service. It spawns child process with specific arguments and waits for its termination. This feature must be used either with authorization or in safe (i.e. when status page is not available world-wide) environment.

For most actions it also extracts user from authentication (if provided) and passes it to the underlying process.
