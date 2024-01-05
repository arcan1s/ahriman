# Recipes

Collection of the examples of docker compose configuration files, which covers some specific cases. Not for production use.

## Configurations

* [Check](check): double process service; one with periodic checks (automatic build disabled) and other one is with the web service.
* [Daemon](daemon): service with periodic repository checks.
* [Distributed](distributed): cluster of three nodes, one with web interface and two workers which are responsible for build process.
* [Distributed manual](distributed-manual): same as [distributed](distributed), but two nodes and update process must be run on worker node manually.
* [i686](i686): non-x86_64 architecture setup.
* [Index](index): repository with index page generator enabled.
* [Multi repo](multirepo): run web service with two separated repositories.
* [OAuth](oauth): web service with OAuth (GitHub provider) authentication enabled.
* [Pull](pull): normal service, but in addition with pulling packages from another source (e.g. GitHub repository).
* [Sign](sign): create repository with database signing.
* [Web](web): simple web service with authentication enabled.
