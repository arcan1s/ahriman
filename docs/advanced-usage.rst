Advanced usage
==============

Depending on the goal the package can be used in different ways. Nevertheless, in the most cases you will need some basic classes

.. code-block:: python

   from pathlib import Path

   from ahriman.core.configuration import Configuration
   from ahriman.core.database import SQLite
   from ahriman.models.repository_id import RepositoryId

   repository_id = RepositoryId("x86_64", "aur-clone")
   configuration = Configuration.from_path(Path("/etc/ahriman.ini"), repository_id)
   database = SQLite.load(configuration)

At this point there are ``configuration`` and ``database`` instances which can be used later at any time anywhere, e.g.

.. code-block:: python

   # instance of ``RepositoryPaths`` class
   paths = configuration.repository_paths

Almost all actions are wrapped by ``ahriman.core.repository.Repository`` class

.. code-block:: python

   from ahriman.core.repository import Repository
   from ahriman.models.pacman_synchronization import PacmanSynchronization

   repository = Repository(repository_id, configuration, database,
                           report=True, refresh_pacman_database=PacmanSynchronization.Disabled)

And the ``repository`` instance can be used to perform repository maintenance

.. code-block:: python

   build_result = repository.process_build(known_packages)
   built_packages = repository.packages_built()
   update_result = repository.process_update(built_packages)

   repository.triggers.on_result(update_result, repository.packages())

For the more info please refer to the classes documentation.
