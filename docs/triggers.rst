Triggers
========

The package provides ability to write custom extensions which will be run on (the most) actions, e.g. after updates. By default ahriman provides two types of extensions - reporting and files uploading. Each extension must derive from the ``Trigger`` class and implement ``run`` method

Trigger example
---------------

Lets consider example of reporting trigger (e.g. `slack <https://slack.com/>`_, which provides easy HTTP API for triggers for integrations).

In order to post message to slack we will need a specific trigger url (something like ``https://hooks.slack.com/services/company_id/trigger_id``), channel (e.g. ``#archrepo``) and username (``repo-bot``). It can be retrieved from the same application instance.

As it has been mentioned, our trigger must derive from specific class

.. code-block:: python

   from ahriman.core.triggers import Trigger

   class SlackReporter(Trigger):

       def __init__(self, architecture, configuration):
           Trigger.__init__(self, architecture, configuration)
           self.slack_url = configuration.get("slack", "url")
           self.channel = configuration.get("slack", "channel")
           self.username = configuration.get("slack", "username")

By now we have class with all required variables.

Lets implement run method. Slack API requires positing data with specific payload by HTTP, thus

.. code-block:: python

   import json
   import requests

   def notify(result, slack_url, channel, username):
       text = f"""Build has been completed with packages: {", ".join([package.name for package in result.success])}"""
       payload = {"channel": channel, "username": username, "text": text}
       response = requests.post(slack_url, data={"payload": json.dumps(payload)})
       response.raise_for_status()

Obviously you can implement the specified method in class, but for guide purpose it has been done as separated method. Now we can merge this method into the class

.. code-block:: python

   class SlackReporter(Trigger):

       def __init__(self, architecture, configuration):
           Trigger.__init__(self, architecture, configuration)
           self.slack_url = configuration.get("slack", "url")
           self.channel = configuration.get("slack", "channel")
           self.username = configuration.get("slack", "username")

       def run(self, result, packages):
           notify(result, self.slack_url, self.channel, self.username)

Setup the trigger
-----------------

First, put the trigger in any path it can be exported, e.g. by packing the resource into python package (which will lead to import path as ``package.slack_reporter.SlackReporter``) or just put file somewhere it can be accessed by application (e.g. ``/usr/local/lib/slack_reporter.py.SlackReporter``.

After that run application as usual and receive notification in your slack channel.
