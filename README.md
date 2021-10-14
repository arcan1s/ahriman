# ArcH Linux ReposItory MANager

[![tests status](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml)
[![setup status](https://github.com/arcan1s/ahriman/actions/workflows/run-setup.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-setup.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/arcan1s/ahriman/badge)](https://www.codefactor.io/repository/github/arcan1s/ahriman)

Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Features

* Install-configure-forget manager for own repository.
* Multi-architecture support.
* VCS packages support.
* Sign support with gpg (repository, package, per package settings).
* Synchronization to remote services (rsync, s3 and github) and report generation (html).
* Dependency manager.
* Ability to patch AUR packages and even create package from local PKGBUILDs.
* Repository status interface with optional authorization and control options:

    ![web interface](web.png)

## Installation and run

For installation details please refer to the [documentation](docs/setup.md). For command help, `--help` subcommand must be used, e.g.:

```shell
$ ahriman --help
usage: ahriman [-h] [-a ARCHITECTURE] [-c CONFIGURATION] [--force] [-l LOCK] [--no-report] [-q] [--unsafe] [-v]
               {aur-search,search,key-import,package-add,add,package-remove,remove,package-status,status,package-status-remove,package-status-update,status-update,patch-add,patch-list,patch-remove,repo-check,check,repo-clean,clean,repo-config,config,repo-init,init,repo-rebuild,rebuild,repo-remove-unknown,remove-unknown,repo-report,report,repo-setup,setup,repo-sign,sign,repo-sync,sync,repo-update,update,user-add,user-remove,web}
               ...

ArcH Linux ReposItory MANager

optional arguments:
  -h, --help            show this help message and exit
  -a ARCHITECTURE, --architecture ARCHITECTURE
                        target architectures (can be used multiple times) (default: None)
  -c CONFIGURATION, --configuration CONFIGURATION
                        configuration path (default: /etc/ahriman.ini)
  --force               force run, remove file lock (default: False)
  -l LOCK, --lock LOCK  lock file (default: /tmp/ahriman.lock)
  --no-report           force disable reporting to web service (default: False)
  -q, --quiet           force disable any logging (default: False)
  --unsafe              allow to run ahriman as non-ahriman user (default: False)
  -v, --version         show program's version number and exit

command:
  {aur-search,search,key-import,package-add,add,package-remove,remove,package-status,status,package-status-remove,package-status-update,status-update,patch-add,patch-list,patch-remove,repo-check,check,repo-clean,clean,repo-config,config,repo-init,init,repo-rebuild,rebuild,repo-remove-unknown,remove-unknown,repo-report,report,repo-setup,setup,repo-sign,sign,repo-sync,sync,repo-update,update,user-add,user-remove,web}
                        command to run
    aur-search (search)
                        search for package
    key-import          import PGP key
    package-add (add)   add package
    package-remove (remove)
                        remove package
    package-status (status)
                        get package status
    package-status-remove
                        remove package status
    package-status-update (status-update)
                        update package status
    patch-add           patches control
    patch-list          patches control
    patch-remove        patches control
    repo-check (check)  check for updates
    repo-clean (clean)  clean local caches
    repo-config (config)
                        dump configuration
    repo-init (init)    create repository tree
    repo-rebuild (rebuild)
                        rebuild repository
    repo-remove-unknown (remove-unknown)
                        remove unknown packages
    repo-report (report)
                        generate report
    repo-setup (setup)  initial service configuration
    repo-sign (sign)    sign packages
    repo-sync (sync)    sync repository
    repo-update (update)
                        update packages
    user-add            create or update user for web services
    user-remove         remove user for web services
    web                 web server
```

Subcommands have own help message as well.

## Configuration

Every available option is described in the [documentation](docs/configuration.md).
