Writing own handler
===================

It is possible to extend the application by adding own custom commands. To do so it is required to implement class, which derives from ``ahriman.application.handlers.handler.Handler`` and put it to the ``ahriman.application.handlers`` package. The class later will be loaded automatically and included to each command run.

Let's imagine, that the new class implements ``help-web``, which prints server information to the stdout. To do so, we need to implement base ``ahriman.application.handlers.handler.Handler.run`` method which is entry point for all subcommands:

.. code-block:: python

   from ahriman.application.application import Application
   from ahriman.application.handlers.handler import Handler


   class HelpWeb(Handler):

      @classmethod
      def run(cls, args: argparse.Namespace, repository_id: RepositoryId, configuration: Configuration, *,
              report: bool) -> None:
        # load application instance
        # report is set to True to make sure that web client is loaded
        application = Application(repository_id, configuration, report=True)
        # extract web client
        client = application.repository.reporter

        # send request to the server
        response = client.make_request("GET", f"{client.address}/api/v1/info")
        result = response.json()
        print(result)

The main functionality of the class is already described, but command is still not available yet. To do so, it is required to set ``arguments`` property, which is the list of the functions, each of them which takes argument parser object, creates new subcommand and returns the modified parser, e.g.:

.. code-block:: python

   import argparse

   from ahriman.application.handlers.handler import SubParserAction

   ...

       @staticmethod
       def set_parser(root: SubParserAction) -> argparse.ArgumentParser:
           parser = root.add_parser("help-web", help="get web server status",
                                    description="request server info and print it to stdout")

       arguments = set_parser

In addition, ``ahriman.application.handlers.handler.Handler.ALLOW_MULTI_ARCHITECTURE_RUN`` can be set to ``False`` in order to disable multiprocess run (e.g. in case if there are conflicting operations, like writting to stdout).

Save the file above as ``/usr/lib/python3.12/site-packages/ahriman/application/handlers/help_web.py`` (replace ``python3.12`` with actual python version) and you are set.

For more examples and details, please check builtin handlers and classes documentations.
