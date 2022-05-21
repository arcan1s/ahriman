Advanced usage
==============

Depending on the goal the package can be used in different ways. Nevertheless, in the most cases you will need some basic classes

.. code-block:: python

   from pathlib import Path

   from ahriman.core.configuration import Configuration
   from ahriman.core.database import SQLite

   architecture = "x86_64"
   configuration = Configuration.from_path(Path("/etc/ahriman.ini"), architecture, quiet=False)
   sqlite = SQLite.load(configuration)

At this point there are ``configuration`` and ``database`` instances which can be used later at any time anywhere, e.g.

.. code-block:: python

   # instance of ``RepositoryPaths`` class
   paths = configuration.repository_paths

Almost all actions are wrapped by ``ahriman.core.repository.Repository`` class

.. code-block:: python

   from ahriman.core.repository import Repository

   repository = Repository(architecture, configuration, database, no_report=False, unsafe=False)

And the ``repository`` instance can be used to perform repository maintenance

.. code-block:: python

   build_result = repository.process_build(known_packages)
   built_packages = repository.packages_built()
   update_result = repository.process_update(built_packages)

   repository.process_triggers(update_result)

For the more info please refer to the classes documentation.
