# ArcH linux ReposItory MANager

[![tests status](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-tests.yml)
[![setup status](https://github.com/arcan1s/ahriman/actions/workflows/run-setup.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/run-setup.yml)
[![docker image](https://github.com/arcan1s/ahriman/actions/workflows/docker-image.yml/badge.svg)](https://github.com/arcan1s/ahriman/actions/workflows/docker-image.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/arcan1s/ahriman/badge)](https://www.codefactor.io/repository/github/arcan1s/ahriman)
[![Documentation Status](https://readthedocs.org/projects/ahriman/badge/?version=latest)](https://ahriman.readthedocs.io/?badge=latest)

Wrapper for managing custom repository inspired by [repo-scripts](https://github.com/arcan1s/repo-scripts).

## Features

* Install-configure-forget manager for own repository.
* Multi-architecture support.
* VCS packages support.
* Sign support with gpg (repository, package, per package settings).
* Synchronization to remote services (rsync, s3 and github) and report generation (email, html, telegram).
* Dependency manager.
* Ability to patch AUR packages and even create package from local PKGBUILDs.
* Repository status interface with optional authorization and control options:

    ![web interface](web.png)

## Installation and run

For installation details please refer to the [documentation](docs/setup.md). For command help, `--help` subcommand must be used. Subcommands have own help message as well. The package also provides a [man page](docs/ahriman.1).

## Configuration

Every available option is described in the [documentation](docs/configuration.md).

## [FAQ](docs/faq.md)
