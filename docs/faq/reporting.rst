Reporting
---------

How to report by email
^^^^^^^^^^^^^^^^^^^^^^

#.
   Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#.
   Configure the service:

   .. code-block:: ini

      [report]
      target = email

      [email]
      host = smtp.example.com
      link_path = http://example.com/aur/x86_64
      password = ...
      port = 465
      receivers = me@example.com
      sender = me@example.com
      user = me@example.com

How to generate index page
^^^^^^^^^^^^^^^^^^^^^^^^^^

#.
   Install dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#.
   Configure the service:

   .. code-block:: ini

      [report]
      target = html

      [html]
      path = ${repository:root}/repository/aur/x86_64/index.html
      link_path = http://example.com/aur/x86_64

Having this configuration, the generated ``index.html`` will be also automatically synced to remote services (e.g. S3).

How to generate RSS feed for index page
"""""""""""""""""""""""""""""""""""""""

In addition to previous steps, the following configuration is required:

.. code-block:: ini

   [report]
   target = html rss

   [html]
   rss_url = ${html:link_path}/rss.xml

   [rss]
   link_path = ${html:link_path}
   path = ${repository:root}/repository/ahriman-demo/x86_64/rss.xml
   rss_url = ${html:link_path}/rss.xml

With the appended configuration, the service fill also generate ``rss.xml``, link it to generated ``index.html`` and put it together.

How to post build report to telegram
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#.
   It still requires additional dependencies:

   .. code-block:: shell

      yay -S --asdeps python-jinja

#.
   Register bot in telegram. You can do it by starting chat with `@BotFather <https://t.me/botfather>`__. For more details please refer to `official documentation <https://core.telegram.org/bots>`__.

#.
   Optionally (if you want to post message in chat):

   #. Create telegram channel.
   #. Invite your bot into the channel.
   #. Make your channel public

#.
   Get chat id if you want to use by numerical id or just use id prefixed with ``@`` (e.g. ``@ahriman``). If you are not using chat the chat id is your user id. If you don't want to make channel public you can use `this guide <https://stackoverflow.com/a/33862907>`__.

#.
   Configure the service:

   .. code-block:: ini

      [report]
      target = telegram

      [telegram]
      api_key = aaAAbbBBccCC
      chat_id = @ahriman
      link_path = http://example.com/aur/x86_64

   ``${api_key}`` is the one sent by `@BotFather <https://t.me/botfather>`__, ``${chat_id}`` is the value retrieved from previous step.

If you did everything fine you should receive the message with the next update. Quick credentials check can be done by using the following command:

.. code-block:: shell

   curl 'https://api.telegram.org/bot${api_key}/sendMessage?chat_id=${chat_id}&text=hello'

(replace ``${chat_id}`` and ``${api_key}`` with the values from configuration).
