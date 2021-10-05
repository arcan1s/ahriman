# ArcH Linux ReposItory MANager

[![build status](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/arcan1s/ahriman/badge)](https://www.codefactor.io/repository/github/arcan1s/ahriman)

Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Features

* Install-configure-forget manager for own repository.
* Multi-architecture support.
* VCS packages support.
* Sign support with gpg (repository, package, per package settings).
* Synchronization to remote services (rsync, s3) and report generation (html).
* Dependency manager.
* Ability to patch AUR packages.
* Repository status interface with optional authorization and control options:

    ![web interface](web.png)

## Installation and run

For installation details please refer to the [documentation](docs/setup.md). For command help, `--help` subcommand must be used, e.g.:

```shell
$ ahriman --help
usage: ahriman [-h] [-a ARCHITECTURE] [-c CONFIGURATION] [--force] [-l LOCK] [--no-log] [--no-report] [--unsafe] [-v]
               {add,check,clean,config,create-user,init,key-import,rebuild,remove,remove-unknown,report,search,setup,sign,status,status-update,sync,update,web} ...

ArcH Linux ReposItory MANager

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHITECTURE, --architecture ARCHITECTURE
                        target architectures (can be used multiple times) (default: None)
  -c CONFIGURATION, --configuration CONFIGURATION
                        configuration path (default: /etc/ahriman.ini)
  --force               force run, remove file lock (default: False)
  -l LOCK, --lock LOCK  lock file (default: /tmp/ahriman.lock)
  --no-log              redirect all log messages to stderr (default: False)
  --no-report           force disable reporting to web service (default: False)
  --unsafe              allow to run ahriman as non-ahriman user (default: False)
  -v, --version         show program's version number and exit

command:
  {add,check,clean,config,create-user,init,key-import,rebuild,remove,remove-unknown,report,search,setup,sign,status,status-update,sync,update,web}
                        command to run
    add                 add package
    check               check for updates
    clean               clean local caches
    config              dump configuration
    create-user         create user for web services
    init                create repository tree
    key-import          import PGP key
    rebuild             rebuild repository
    remove              remove package
    remove-unknown      remove unknown packages
    report              generate report
    search              search for package
    setup               initial service configuration
    sign                sign packages
    status              get package status
    status-update       update package status
    sync                sync repository
    update              update packages
    web                 start web server
```

Subcommands have own help message as well.

## Configuration

Every available option is described in the [documentation](docs/configuration.md).
