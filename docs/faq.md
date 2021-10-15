# FAQ

## General topics

### What is the purpose of the project?

This project has been created in order to maintain self-hosted Arch Linux user repository without manual intervention - checking for updates and building packages.

### How do I install it?

TL;DR

```shell
yay -S ahriman
sudo -u ahriman ahriman -a x86_64 init
sudo ahriman -a x86_64 repo-setup --packager "ahriman bot <ahriman@example.com>" --repository "repository"
systemctl enable --now ahriman@x86_64.timer
```

#### Long answer

The idea is to install the package as usual, create working directory tree, create configuration for `sudo` and `devtools`. Detailed description of the setup instruction can be found [here](setup.md).

### Okay, I've installed ahriman, how do I add new package?

```shell
sudo -u ahriman ahriman package-add ahriman --now
```

`--now` flag is totally optional and just run `repo-update` subcommand after the registering the new package, Thus the extended flow is the following:

```shell
sudo -u ahriman ahriman package-add ahriman
sudo -u ahriman ahriman repo-update
```

### AUR is fine, but I would like to create package from local PKGBUILD

TL;DR

```shell
sudo -u ahriman ahriman package-add /path/to/local/directory/with/PKGBUILD --now
```

Before using this command you will need to create local directory, put `PKGBUILD` there and generate `.SRCINFO` by using `makepkg --printsrcinfo > .SRCINFO` command. These packages will be stored locally and _will be ignored_ during automatic update; in order to update the package you will need to run `package-add` command again.

### But I just wanted to change PKGBUILD from AUR a bit!

Well it is supported also.

1. Clone sources from AUR.
2. Make changes you would like to (e.g. edit `PKGBUILD`, add external patches).
3. Run `sudo -u ahriman ahriman patch-add /path/to/local/directory/with/PKGBUILD`.

The last command will calculate diff from current tree to the `HEAD` and will store it locally. Patches will be applied on any package actions (e.g. it can be used for dependency management).

### Package build fails because it cannot validate PGP signature of source files

TL;DR

```shell
sudo -u ahriman ahriman key-import ...
```

### How do I check if there are new commits for VCS packages?

Normally the service handles VCS packages correctly, but it requires additional dependencies:

```shell
pacman -S breezy darcs mercurial subversion
```

### I would like to remove package because it is no longer needed/moved to official repositories

```shell
sudo -u ahriman ahriman package-remove ahriman
```

Also, there is command `repo-remove-unknown` which checks packages in AUR and local storage and removes ones which have been removed.

Remove commands also remove any package files (patches, caches etc).

### There is new major release of %library-name%, how do I rebuild packages?

TL;DR

```shell
sudo -u ahriman ahriman repo-rebuild --depends-on python
```

You can even rebuild the whole repository (which is particular useful in case if you would like to change packager) if you do not supply `--depends-on` option.

However, note that you do not need to rebuild repository in case if you just changed signing option, just use `repo-sign` command instead. 

### Hmm, I have packages built, but how can I use it?

Add the following lines to your `pacman.conf`:

```ini
[repository]
Server = file:///var/lib/ahriman/repository/x86_64
```

(You might need to add `SigLevel` option according to the pacman documentation.)

## Remote synchronization

### Wait I would like to use the repository from another server

There are several choices:

1. Easy and cheap, just share your local files through the internet, e.g. for `nginx`:
   
    ```
    server {
        location /x86_64 {
            root /var/lib/ahriman/repository/x86_64;
            autoindex on;
        }
    }
    ```
   
2. You can also upload your packages using `rsync` to any available server. In order to use it you would need to configure ahriman first:
    
    ```ini
    [upload]
    target = rsync
    
    [rsync]
    remote = 192.168.0.1:/srv/repo
    ```
   
    After that just add `/srv/repo` to the `pacman.conf` as usual. You can also upload to S3 (e.g. `Server = https://s3.eu-central-1.amazonaws.com/repository/x86_64`) or to Github (e.g. `Server = https://github.com/ahriman/repository/releases/download/x86_64`).

### How do I configure S3?

1. Install dependencies:

   ```shell
   pacman -S python-boto3
   ```

3. Create a bucket.
4. Create user with write access to the bucket:

    ```
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
    ```

5. Create an API key for the user and store it.
6. Configure the service as following:

    ```ini
    [upload]
    target = s3

    [s3]
    access_key = ...
    bucket = repository
    region = eu-central-1
    secret_key = ...
    ```
   
### How do I configure Github?

1. Create a repository.
2. [Create API key](https://github.com/settings/tokens) with scope `public_repo`.
3. Configure the service as following:

    ```ini
    [upload]
    target = github

    [github]
    owner = ahriman
    password = ...
    repository = repository
    username = ahriman
    ```

## Reporting

### I would like to get report to email

1. Install dependencies:

   ```shell
   yay -S python-jinja
   ```
   
2. Configure the service:

   ```ini
   [report]
   target = email
   
   [email]
   host = smtp.example.com
   link_path = http://example.com/x86_64
   password = ...
   port = 465
   receivers = me@example.com
   sender = me@example.com
   user = me@example.com
   ```
   
### I'm using synchronization to S3 and would like to generate index page

1. Install dependencies:

   ```shell
   yay -S python-jinja
   ```
   
2. Configure the service:
   
   ```ini
   [report]
   target = html
   
   [html]
   path = /var/lib/ahriman/repository/x86_64/index.html
   link_path = http://example.com/x86_64
   ```
   
After these steps `index.html` file will be automatically synced to S3

## Web service

### Readme mentions web interface, how do I use it?

1. Install dependencies:

   ```shell
   yay -S python-aiohttp python-aiohttp-jinja2
   ```

2. Configure service:

   ```ini
   [web]
   port = 8080
   ```

3. Start the web service `systemctl enable --now ahriman-web@x86_64`.

### I would like to limit user access to the status page

1. Install dependencies 😊:
   
   ```shell
   yay -S python-aiohttp-security python-aiohttp-session python-cryptography
   ```

2. Configure the service to enable authorization:

   ```ini
   [auth]
   target = configuration
   ```
   
3. Create user for the service:

   ```shell
   sudo -u ahriman ahriman user-add --as-service -r write api
   ```
   
   This command will ask for the password, just type it in stdin; _do not_ leave the field blank, user will not be able to authorize.

4. Create end-user `sudo -u ahriman ahriman user-add -r write my-first-user` with password.
5. Restart web service `systemctl restart ahriman-web@x86_64`.

### I would like to use OAuth

1. Create OAuth web application, download its `client_id` and `client_secret`.
2. Guess what? Install dependencies:

   ```shell
   yay -S python-aiohttp-security python-aiohttp-session python-cryptography python-aioauth-client
   ```
   
3. Configure the service:

   ```ini
   [auth]
   target = oauth
   client_id = ...
   client_secret = ...
   
   [web]
   address = https://example.com
   ```
   
   Configure `oauth_provider` and `oauth_scopes` in case if you would like to use different from Google provider. Scope must grant access to user email. `web.address` is required to make callback URL available from internet.

4. Create service user:

   ```shell
   sudo -u ahriman ahriman user-add --as-service -r write api
   ```

5. Create end-user `sudo -u ahriman ahriman user-add -r write my-first-user`. When it will ask for the password leave it blank.
6. Restart web service `systemctl restart ahriman-web@x86_64`.

## Other topics

### How does it differ from %another-manager%?

Short answer - I do not know.

#### [archrepo2](https://github.com/lilydjwg/archrepo2)

Don't know, haven't tried it. But it lacks of documentation at least.

* Web interface.
* No synchronization and reporting.
* `archrepo2` actively uses direct shell calls and `yaourt` components.
* It has constantly running process instead of timer process (it is not pro or con).

#### [repo-scripts](https://github.com/arcan1s/repo-scripts)

Though originally I've created ahriman by trying to improve the project, it still lacks a lot of features:

* Web interface.
* Better reporting with template support.
* Synchronization features (there was only `rsync` based).
* Local packages and patches support.
* No dependency management.
* And so on.

`repo-scripts` also have bad architecture and bad quality code and uses out-of-dated `yaourt` and `package-query`.

### I would like to check service logs

By default, the service writes logs to `/dev/log` which can be accessed by using `journalctl` command (logs are written to the journal of the user under which command is run).

You can also edit configuration and forward logs to `stderr`, just change `handlers` value, e.g.:

```shell
sed -i 's/handlers = syslog_handler/handlers = console_handler/g' /etc/ahriman.ini.d/logging.ini
```

You can even configure logging as you wish, but kindly refer to python `logging` module configuration.

### Html customization

It is possible to customize html templates. In order to do so, create files somewhere (refer to Jinja2 documentation and the service source code for available parameters) and put `template_path` to configuration pointing to this directory.

### I did not find my question

[Create an issue](https://github.com/arcan1s/ahriman/issues) with type **Question**.
