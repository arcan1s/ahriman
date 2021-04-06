# ahriman configuration

Some groups can be specified for each architecture separately. E.g. if there are `build` and `build:x86_64` groups it will use the option from `build:x86_64` for the `x86_64` architecture and `build` for any other (architecture specific group has higher priority). In case if both groups are presented, architecture specific options will be merged into global ones overriding them. 

## `settings` group

Base configuration settings.

* `include` - path to directory with configuration files overrides, string, required.
* `logging` - path to logging configuration, string, required. Check `logging.ini` for reference.

## `alpm` group

libalpm and AUR related configuration.

* `aur_url` - base url for AUR, string, required.
* `database` - path to pacman local database cache, string, required.
* `repositories` - list of pacman repositories, space separated list of strings, required.
* `root` - root for alpm library, string, required.

## `build:*` groups

Build related configuration. Group name must refer to architecture, e.g. it should be `build:x86_64` for x86_64 architecture.

* `archbuild_flags` - additional flags passed to `archbuild` command, space separated list of strings, optional.
* `build_command` - default build command, string, required.
* `ignore_packages` - list packages to ignore during a regular update (manual update will still work), space separated list of strings, optional.
* `makepkg_flags` - additional flags passed to `makepkg` command, space separated list of strings, optional.
* `makechrootpkg_flags` - additional flags passed to `makechrootpkg` command, space separated list of strings, optional.

## `repository` group

Base repository settings.

* `name` - repository name, string, required.
* `root` - root path for application, string, required.

## `sign:*` groups

Settings for signing packages or repository. Group name must refer to architecture, e.g. it should be `sign:x86_64` for x86_64 architecture.

* `target` - configuration flag to enable signing, space separated list of strings, required. Allowed values are `package` (sign each package separately), `repository` (sign repository database file).
* `key` - default PGP key, string, required. This key will also be used for database signing if enabled.
* `key_*` settings - PGP key which will be used for specific packages, string, optional. For example, if there is `key_yay` option the specified key will be used for yay package and default key for others.

## `report` group

Report generation settings.

* `target` - list of reports to be generated, space separated list of strings, optional. Allowed values are `html`, `email`.

### `email:*` groups

Group name must refer to architecture, e.g. it should be `email:x86_64` for x86_64 architecture.

* `homepage` - link to homepage, string, optional.
* `host` - SMTP host for sending emails, string, required.
* `link_path` - prefix for HTML links, string, required.
* `password` - SMTP password to authenticate, string, optional.
* `port` - SMTP port for sending emails, int, required.
* `receivers` - SMTP receiver addresses, space separated list of strings, required.
* `sender` - SMTP sender address, string, required.
* `ssl` - SSL mode for SMTP connection, one of `ssl`, `starttls`, `disabled`, optional, default `disabled`.
* `template_path` - path to Jinja2 template, string, required.
* `user` - SMTP user to authenticate, string, optional.

### `html:*` groups

Group name must refer to architecture, e.g. it should be `html:x86_64` for x86_64 architecture.

* `path` - path to html report file, string, required.
* `homepage` - link to homepage, string, optional.
* `link_path` - prefix for HTML links, string, required.
* `template_path` - path to Jinja2 template, string, required.

## `upload` group

Remote synchronization settings.

* `target` - list of synchronizations to be used, space separated list of strings, optional. Allowed values are `rsync`, `s3`.

### `rsync:*` groups

Group name must refer to architecture, e.g. it should be `rsync:x86_64` for x86_64 architecture. Requires `rsync` package to be installed. Do not forget to configure ssh for user `ahriman`.

* `command` - rsync command to run, space separated list of string, required.
* `remote` - remote server to rsync (e.g. `1.2.3.4:5678:path/to/sync`), string, required.

### `s3:*` groups

Group name must refer to architecture, e.g. it should be `s3:x86_64` for x86_64 architecture. Requires `aws-cli` package to be installed. Do not forget to configure it for user `ahriman`.

* `command` - s3 command to run, space separated list of string, required.
* `bucket` - bucket name (e.g. `s3://bucket/path`), string, required.

## `web:*` groups

Web server settings. If any of `host`/`port` is not set, web integration will be disabled. Group name must refer to architecture, e.g. it should be `web:x86_64` for x86_64 architecture.

* `host` - host to bind, string, optional.
* `port` - port to bind, int, optional.
* `templates` - path to templates directory, string, required.
