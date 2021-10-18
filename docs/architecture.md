# Package structure

Packages have strict rules of importing:

* `ahriman.application` package must not be used anywhere except for itself.
* `ahriman.core` and `ahriman.models` packages don't have any import restriction. Actually we would like to totally restrict importing of `core` package from `models`, but it is impossible at the moment.
* `ahriman.web` package is allowed to be imported from `ahriman.application` (web handler only, only `ahriman.web.web` methods). It also must not be imported globally, only local import is allowed. 

Full dependency diagram:

![architecture](ahriman-architecture.svg)

## `ahriman.application` package

This package contains application (aka executable) related classes and everything for that. It also contains package called `ahriman.application.handlers` in which all available subcommands are described as separated classes derived from base `ahriman.application.handlers.handler.Handler` class. `ahriman.application.ahriman` contains only command line parses and executes specified `Handler` on success, `ahriman.application.application.Application` is a god class which provides interfaces for all repository related actions. `ahriman.application.lock.Lock` is additional class which provides file-based lock and also performs some common checks.

## `ahriman.core` package

This package contains everything which is required for any time of application run and separated to several packages:

* `ahriman.core.alpm` package controls pacman related functions. It provides wrappers for `pyalpm` library and safe calls for repository tools (`repo-add` and `repo-remove`).
* `ahriman.core.auth` package provides classes for authorization methods used by web mostly. Base class is `ahriman.core.auth.auth.Auth` which must be called by `load` method.
* `ahriman.core.build_tools` is a package which provides wrapper for `devtools` commands.
* `ahriman.core.report` is a package with reporting classes. Usually it must be called by `ahriman.core.report.report.Report.load` method.
* `ahriman.core.repository` contains several traits and base repository (`ahriman.core.repository.repository.Repository` class) implementation.
* `ahriman.core.sign` package provides sign feature (only gpg calls are available).
* `ahriman.core.status` contains helpers and watcher class which are required for web application. Reporter must be initialized by using `ahriman.core.status.client.Client.load` method.
* `ahriman.core.upload` package provides sync feature, must be called by `ahriman.core.upload.upload.Upload.load` method.

This package also provides some generic functions and classes which may be used by other packages:

* `ahriman.core.configuration.Configuration` is an extension for standard `configparser` library.
* `ahriman.core.exceptions` provides custom exceptions.
* `ahriman.core.spawn.Spawn` is a tool which can spawn another `ahriman` process. This feature is used by web application.
* `ahriman.core.tree` is a dependency tree implementation.

## `ahriman.models` package

It provides models for any other part of application. Unlike `ahriman.core` package classes from here provides only conversion methods (e.g. create class from another or convert to). Mostly case classes and enumerations.

## `ahriman.web` package

Web application. It is important that this package is isolated from any other to allow it to be optional feature (i.e. dependencies which are required by the package are optional).

* `ahriman.web.middlewares` provides middlewares for request handlers.
* `ahriman.web.views` contains web views derived from aiohttp view class.
* `ahriman.web.routes` creates routes for web application.
* `ahriman.web.web` provides main web application functions (e.g. start, initialization).

# Application run

* Parse command line arguments, find command and related handler which is set by parser.
* Call `Handler.execute` method.
* Define list of architectures to run. In case if there is more than one architecture specified run several subprocesses or process in current process otherwise. Class attribute `ALLOW_MULTI_ARCHITECTURE_RUN` controls whether application can be run in multiple processes or not - this feature is required for some handlers (e.g. `Web`) which should be able to spawn child process in daemon mode (it is impossible to do for daemonic processes).
* In each child process call lock functions.
* After success checks pass control to `Handler.run` method defined by specific handler class.
* Return result (success or failure) of each subprocess and exit from application.

In most cases handlers spawn god class `ahriman.application.application.Application` class and call required methods.

Application is designed to run from `systemd` services and provides parametrized by architecture timer and service file for that.

# Basic flows

## Add new packages or rebuild existing

Idea is to copy package to the directory from which it will be handled at the next update run. Different variants are supported:

* If supplied argument is file then application moves the file to the directory with built packages. Same rule applies for directory, but in this case it copies every package-like file from the specified directory.
* If supplied argument is directory and there is `PKGBUILD` file there it will be treated as local package. In this case it will queue this package to build and copy source files (`PKGBUILD` and `.SRCINFO`) to caches.
* If supplied argument iis not file then application tries to lookup for the specified name in AUR and clones it into the directory with manual updates. This scenario can also handle package dependencies which are missing in repositories.

This logic can be overwritten by specifying the `source` parameter, which is partially useful if you would like to add package from AUR, but there is local directory cloned from AUR.

## Rebuild packages

Same as add function for every package in repository. Optional filter by reverse dependency can be supplied.

## Remove packages

This flow removes package from filesystem, updates repository database and also runs synchronization and reporting methods.

## Update packages

This feature is divided into to stages: check AUR for updates and run rebuild for required packages. Whereas check does not do anything except for check itself, update flow is the following:

1. Process every built package first. Those packages are usually added manually.
2. Run sync and report methods.
3. Generate dependency tree for packages to be built.
4. For each level of tree it does:
   1. Download package data from AUR.
   2. Build every package in clean chroot.
   3. Sign packages if required.
   4. Add packages to database and sign database if required.
   5. Process sync and report methods.

After any step any package data is being removed.

# Core functions reference

## Configuration 

`ahriman.core.configuration.Configuration` class provides some additional methods (e.g. `getpath` and `getlist`) and also combines multiple files into single configuration dictionary using architecture overrides. It is the recommended way to deal with settings.

## Utils

For every external command run (which is actually not recommended if possible) custom wrapper for `subprocess` is used. Additional functions `ahriman.core.auth.helpers` provide safe calls for `aiohttp_security` methods and are required to make this dependency optional.

## Submodules

Some packages provide different behaviour depending on configuration settings. In these cases inheritance is used and recommended way to deal with them is to call class method `load` from base classes.

## Authorization

The package provides several authorization methods: disabled, based on configuration and OAuth2. 

Disabled (default) authorization provider just allows everything for everyone and does not have any specific configuration (it uses some default configuration parameters though). It also provides generic interface for derived classes.

Mapping (aka configuration) provider uses hashed passwords with salt from configuration file in order to authenticate users. This provider also enables user permission checking (read/write) (authorization). Thus, it defines the following methods:

* `check_credentials` - user password validation (authentication).
* `verify_access` - user permission validation (authorization).

Passwords must be stored in configuration as `hash(password + salt)`, where `password` is user defined password (taken from user input), `salt` is random string (any length) defined globally in configuration and `hash` is secure hash function. Thus, the following configuration

```ini
[auth:read]
username = $6$rounds=656000$mWBiecMPrHAL1VgX$oU4Y5HH8HzlvMaxwkNEJjK13ozElyU1wAHBoO/WW5dAaE4YEfnB0X3FxbynKMl4FBdC3Ovap0jINz4LPkNADg0
```

means that there is user `username` with `read` access and password `password` hashed by `sha512` with salt `salt`.

OAuth provider uses library definitions (`aioauth-client`) in order _authenticate_ users. It still requires user permission to be set in configuration, thus it inherits mapping provider without any changes. Whereas we could override `check_credentials` (authentication method) by something custom, OAuth flow is a bit more complex than just forward request, thus we have to implement the flow in login form.

OAuth's implementation also allows authenticating users via username + password (in the same way as mapping does) though it is not recommended for end-users and password must be left blank. In particular this feature is used by service reporting (aka robots).

In order to configure users there are special commands.

## Remote synchronization

There are several supported synchronization providers, currently they are `rsync`, `s3`, `github`. 

`rsync` provider does not have any specific logic except for running external rsync application with configured arguments. The service does not handle SSH configuration, thus it has to be configured before running application manually.

`s3` provider uses `boto3` package and implements sync feature. The files are stored in architecture directory (e.g. if bucket is `repository`, packages will be stored in `repository/x86_64` for the `x86_64` architecture), bucket must be created before any action and API key must have permissions to write to the bucket. No external configuration required. In order to upload only changed files the service compares calculated hashes with the Amazon ETags, used realization is described [here](https://teppen.io/2018/10/23/aws_s3_verify_etags/). 

`github` provider authenticates through basic auth, API key with repository write permissions is required. There will be created a release with the name of the architecture in case if it does not exist; files will be uploaded to the release assets. It also stores array of files and their MD5 checksums in release body in order to upload only changed ones. According to the Github API in case if there is already uploaded asset with the same name (e.g. database files), asset will be removed first.

## Additional features

Some features require optional dependencies to be installed:

* Version control executables (e.g. `git`, `svn`) for VCS packages.
* `gnupg` application for package and repository sign feature.
* `rsync` application for rsync based repository sync.
* `boto3` python package for `S3` sync.
* `Jinja2` python package for HTML report generation (it is also used by web application).

# Web application

Web application requires the following python packages to be installed:

* Core part requires `aiohttp` (application itself), `aiohttp_jinja2` and `Jinja2` (HTML generation from templates).
* In addition, `aiohttp_debugtoolbar` is required for debug panel. Please note that this option does not work together with authorization and basically must not be used in production.
* In addition, authorization feature requires `aiohttp_security`, `aiohttp_session` and `cryptography`.
* In addition to base authorization dependencies, OAuth2 also requires `aioauth-client` library.

## Middlewares

Service provides some custom middlewares, e.g. logging every exception (except for user ones) and user authorization.

## Web views

All web views are defined in separated package and derived from `ahriman.web.views.base.Base` class which provides typed interfaces for web application. 

REST API supports both form and JSON data, but the last one is recommended. 

Different APIs are separated into different packages:

* `ahriman.web.views.service` provides views for application controls.
* `ahriman.web.views.status` package provides REST API for application reporting.
* `ahriman.web.views.user` package provides login and logout methods which can be called without authorization.

## Templating

Package provides base jinja templates which can be overridden by settings. Vanilla templates are actively using bootstrap library.

## Requests and scopes

Service provides optional authorization which can be turned on in settings. In order to control user access there are two levels of authorization - read-only (only GET-like requests) and write (anything) which are provided by each web view directly.

If this feature is configured any request will be prohibited without authentication. In addition, configuration flag `auth.safe_build_status` can be used in order to allow seeing main page without authorization.

For authenticated users it uses encrypted session cookies to store tokens; encryption key is generated each time at the start of the application. It also stores expiration time of the session inside.

## External calls

Web application provides external calls to control main service. It spawns child process with specific arguments and waits for its termination. This feature must be used either with authorization or in safe (i.e. when status page is not available world-wide) environment.
