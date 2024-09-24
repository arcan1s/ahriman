Remote synchronization
----------------------

How to sync repository to another server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several choices:

#.
   Easy and cheap, just share your local files through the internet, e.g. for ``nginx``:

   .. code-block::

       server {
           location / {
               autoindex on;
               root /var/lib/ahriman/repository/;
           }
       }

#.
   You can also upload your packages using ``rsync`` to any available server. In order to use it you would need to configure ahriman first:

   .. code-block:: ini

       [upload]
       target = rsync

       [rsync]
       remote = 192.168.0.1:/srv/repo

   After that just add ``/srv/repo`` to the ``pacman.conf`` as usual. You can also upload to S3 (``Server = https://s3.eu-central-1.amazonaws.com/repository/aur/x86_64``) or to GitHub (``Server = https://github.com/ahriman/repository/releases/download/aur-x86_64``).

How to sync to S3
^^^^^^^^^^^^^^^^^

#.
   Install dependencies:

   .. code-block:: shell

      pacman -S python-boto3

#.
   Create a bucket (e.g. ``repository``).

#.
   Create an user with write access to the bucket:

   .. code-block::

       {
           "Version": "2012-10-17",
           "Statement": [
               {
                   "Sid": "ListObjectsInBucket",
                   "Effect": "Allow",
                   "Action": [
                       "s3:ListBucket"
                   ],
                   "Resource": [
                       "arn:aws:s3:::repository"
                   ]
               },
               {
                   "Sid": "AllObjectActions",
                   "Effect": "Allow",
                   "Action": "s3:*Object",
                   "Resource": [
                       "arn:aws:s3:::repository/*"
                   ]
               }
           ]
       }

#.
   Create an API key for the user and store it.

#.
   Configure the service as following:

   .. code-block:: ini

       [upload]
       target = s3

       [s3]
       access_key = ...
       bucket = repository
       region = eu-central-1
       secret_key = ...

S3 with SSL
"""""""""""

In order to configure S3 on custom domain with SSL (and some other features, like redirects), the CloudFront should be used.

#. Configure S3 as described above.
#. In bucket properties, enable static website hosting with hosting type "Host a static website".
#. Go to AWS Certificate Manager and create public certificate on your domain. Validate domain as suggested.
#. Go to CloudFront and create distribution. The following settings are required:

   * Origin domain choose S3 bucket.
   * Tick use website endpoint.
   * Disable caching.
   * Select issued certificate.

#. Point DNS record to CloudFront address.

How to sync to GitHub releases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#.
   Create a repository.

#.
   `Create API key <https://github.com/settings/tokens>`__ with scope ``public_repo``.

#.
   Configure the service as following:

   .. code-block:: ini

       [upload]
       target = github

       [github]
       owner = ahriman
       password = ...
       repository = repository
       username = ahriman
