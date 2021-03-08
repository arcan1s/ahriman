# ahriman configuration

Some groups can be specified for each architecture separately with default values. E.g. if there are `build` and `build_x86_64` groups it will use the `build_x86_64` for the `x86_64` architecture and `build` for any other.

## `settings` group

Base configuration settings:

* `include` - path to directory with configuration files overrides, string, required.
* `logging` - path to logging configuration, string, required. Check `logging.ini` for reference.

## `aur` group

AUR related configuration:

* `url` - base url for AUR, string, required.

## `build_*` groups

Build related configuration. Group name must refer to architecture, e.g. it should be `build_x86_64` for x86_64 architecture.

* `archbuild_flags` - additional flags passed to `archbuild` command, space separated list of strings, optional.
* `build_command` - default build command, string, required.
* `ignore_packages` - list packages to ignore during a regular update (manual update will still work), space separated list of strings, optional.
* `makepkg_flags` - additional flags passed to `makepkg` command, space separated list of strings, optional.
* `makechrootpkg_flags` - additional flags passed to `makechrootpkg` command, space separated list of strings, optional.

## `repository` group

Base repository settings:

* `name` - repository name, string, required.
* `root` - root path for application, string, required.

## `sign` group

Settings for signing packages or repository:

* `enabled` - configuration flag to enable signing, string, required. Allowed values are `disabled`, `package` (sign each package separately), `repository` (sign repository database file).
* `key` - PGP key, string, optional.

## `report` group

Report generation settings:

* `target` - list of reports to be generated, space separated list of strings, optional. Allowed values are `html`.

### `html_*` group

Group name must refer to architecture, e.g. it should be `html_x86_64` for x86_64 architecture.

* `path` - path to html report file, string, required.
* `homepage` - link to homepage, string, optional.
* `link_path` - prefix for HTML links, string, required.
* `template_path` - path to Jinja2 template, string, required.

## `upload` group

Remote synchronization settings:

* `target` - list of synchronizations to be used, space separated list of strings, optional. Allowed values are `rsync`, `s3`.

### `s3_*` group

Group name must refer to architecture, e.g. it should be `s3_x86_64` for x86_64 architecture. Requires `aws-cli` package to be installed. Do not forget to configure it for user `ahriman`.

* `bucket` - bucket name (e.g. `s3://bucket/path`), string, required.

### `rsync_*` group

Group name must refer to architecture, e.g. it should be `rsync_x86_64` for x86_64 architecture. Requires `rsync` package to be installed. Do not forget to configure ssh for user `ahriman`.

* `remote` - remote server to rsync (e.g. `1.2.3.4:5678:path/to/sync`), string, required.
