Triggers
========

The package provides ability to write custom extensions which will be run on (the most) actions, e.g. after updates. By default ahriman provides three types of extensions - reporting, files uploading and PKGBUILD syncronization. Each extension must derive from the ``ahriman.core.triggers.Trigger`` class and should implement at least one of the abstract methods:

* ``on_result`` - trigger action which will be called after build process, the build result and the list of repository packages will be supplied as arguments.
* ``on_start`` - trigger action which will be called right before the start of the application process.
* ``on_stop`` - action which will be called right before the exit.

Note, it isn't required to implement all of those methods (or even one of them), however, it is highly recommended to avoid trigger actions in ``__init__`` method as it will be run on any application start (e.g. even if you are just searching in AUR).

Built-in triggers
-----------------

For the configuration details and settings explanation kindly refer to the :doc:`documentation <configuration>`.

``ahriman.core.gitremote.RemotePullTrigger``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This trigger will be called before any action (``on_start``) and pulls remote PKGBUILD repository locally; after that it copies found PKGBUILDs from the cloned repository to the local cache. It is useful in case if you have patched PGKBUILDs (or even missing in AUR) which you would like to use for package building and, technically, just simplifies the local package building.

In order to update those packages you would need to clone your repository separately, make changes in PKGBUILD (e.g. bump version and update checksums), commit them and push back. On the next ahriman's repository update, it will pull changes you committed and will perform package update.

``ahriman.core.gitremote.RemotePushTrigger``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This trigger will be called right after build process (``on_result``). It will pick PKGBUILDs for the updated packages, pull them (together with any other files) and commit and push changes to remote repository. No real use cases, but the most of user repositories do it.

``ahriman.core.report.ReportTrigger``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Trigger which can be used for reporting. It implements ``on_result`` method and thus being called on each build update and generates report (e.g. html, telegram etc) according to the current settings.

``ahriman.core.upload.UploadTrigger``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This trigger takes build result (``on_result``) and performs syncing of the local packages to the remote mirror (e.g. S3 or just by rsync).

Context variables
-----------------

By default, only configuration and architecture are passed to triggers. However, some triggers might want to have access to other high-level wrappers. In order to provide such ability and avoid (double) initialization, the service provides a global context variables, which can be accessed from ``ahriman.core`` package:

.. code-block:: python

   from ahriman.core import context

   ctx = context.get()

Just because context is wrapped inside ``contexvars.ContextVar``, you need to explicitly extract variable by ``get()`` method. Later you can extract any variable if it is set, e.g.:

.. code-block:: python

   from ahriman.core.database import SQLite
   from ahriman.models.context_key import ContextKey

   database = ctx.get(ContextKey("database", SQLite))

In order to provide typed API, all variables are stored together with their type. The ``get(ContextKey)`` method will throw ``KeyError`` in case if key is missing. Alternatively you can set your own variable inside context:

.. code-block:: python

   ctx.set(ContextKey("answer", int), 42)
   context.set(ctx)

Note, however, that there are several limitations:

* Context variables are immutable, thus you cannot override value if the key already presented.
* The ``return_type`` of ``ContextKey`` should match the value type, otherwise exception will be thrown.

The ``context`` also implements collection methods such as ``__iter__`` and ``__len__``.

Trigger example
---------------

Lets consider example of reporting trigger (e.g. `slack <https://slack.com/>`_, which provides easy HTTP API for integration triggers).

In order to post message to slack we will need a specific trigger url (something like ``https://hooks.slack.com/services/company_id/trigger_id``), channel (e.g. ``#archrepo``) and username (``repo-bot``).

As it has been mentioned, our trigger must derive from specific class:

.. code-block:: python

   from ahriman.core.triggers import Trigger

   class SlackReporter(Trigger):

       def __init__(self, architecture, configuration):
           Trigger.__init__(self, architecture, configuration)
           self.slack_url = configuration.get("slack", "url")
           self.channel = configuration.get("slack", "channel")
           self.username = configuration.get("slack", "username")

By now we have class with all required variables. Lets implement run method. Slack API requires positing data with specific payload by HTTP, thus:

.. code-block:: python

   import json
   import requests

   def notify(result, slack_url, channel, username):
       text = f"""Build has been completed with packages: {", ".join([package.name for package in result.success])}"""
       payload = {"channel": channel, "username": username, "text": text}
       response = requests.post(slack_url, data={"payload": json.dumps(payload)})
       response.raise_for_status()

Obviously you can implement the specified method in class, but for guide purpose it has been done as separated method. Now we can merge this method into the class:

.. code-block:: python

   class SlackReporter(Trigger):

       def __init__(self, architecture, configuration):
           Trigger.__init__(self, architecture, configuration)
           self.slack_url = configuration.get("slack", "url")
           self.channel = configuration.get("slack", "channel")
           self.username = configuration.get("slack", "username")

       def on_result(self, result, packages):
           notify(result, self.slack_url, self.channel, self.username)

Setup the trigger
^^^^^^^^^^^^^^^^^

First, put the trigger in any path it can be exported, e.g. by packing the resource into python package (which will lead to import path as ``package.slack_reporter.SlackReporter``) or just put file somewhere it can be accessed by application (e.g. ``/usr/local/lib/slack_reporter.py.SlackReporter``).

After that run application as usual and receive notification in your slack channel.

Trigger configuration schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Triggers can expose their configuration schema. It can be achieved by implementing ``CONFIGURATION_SCHEMA`` class variable according to `cerberus <https://docs.python-cerberus.org/>`_ documentation. For more details and examples, please refer to built-in triggers implementations.
