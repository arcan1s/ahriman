Basic usage
===========

Depending on the goal the package can be used in different ways. Nevertheless, in the most cases you will need some basic classes::

    from pathlib import Path

    from ahriman.core.configuration import Configuration
    from ahriman.core.database.sqlite import SQLite

    architecture = "x86_64"
    configuration = Configuration.from_path(Path("/etc/ahriman.ini"), architecture, quiet=False)
    sqlite = SQLite.load(configuration)

At this point there are ``configuration`` and ``database`` instances which can be used later at any time anywhere, e.g.::

    # instance of ``RepositoryPaths`` class
    paths = configuration.repository_paths

Almost all actions are wrapped by ``ahriman.core.repository.Repository`` class::

    from ahriman.core.repository import Repository

    repository = Repository(architecture, configuration, database, no_report=False, unsafe=False)

And the ``repository`` instance can be used to perform repository maintenance::

    build_result = repository.process_build(known_packages)
    built_packages = repository.packages_built()
    update_result = repository.process_update(built_packages)

    repository.process_report(None, update_result)
    repository.process_sync(None, update_result.success)
