Welcome to ahriman's documentation!
===================================

Wrapper for managing custom repository inspired by `repo-scripts <https://github.com/arcan1s/repo-scripts>`_.

Features
--------

* Install-configure-forget manager for the very own repository.
* Multi architecture and repository support.
* Dependency manager.
* VCS packages support.
* Official repository support.
* Ability to patch AUR packages and even create package from local PKGBUILDs.
* Various rebuild options with ability to automatically bump package version.
* Sign support with gpg (repository, package), multiple packagers support.
* Triggers for repository updates, e.g. synchronization to remote services (rsync, S3 and GitHub) and report generation (email, html, telegram).
* Repository status interface with optional authorization and control options.

Live demos
----------

* `Build status page <https://ahriman-demo.arcanis.me>`_. You can login as ``demo`` user by using ``demo`` password. Note, however, you will not be able to run tasks. `HTTP API documentation <https://ahriman-demo.arcanis.me/api-docs>`_ is also available.
* `Repository index <https://repo.arcanis.me/x86_64/index.html>`_.
* `Telegram feed <https://t.me/arcanisrepo>`_.

Contents
--------

.. toctree::
   :maxdepth: 2

   setup
   configuration
   command-line
   faq
   migration
   architecture
   advanced-usage
   triggers
   modules
