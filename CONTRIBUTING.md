# Contributing to ahriman

Welcome to ahriman! The goal of the project is to provide the best user experience to manage Archlinux repositories. In order to follow this we set some limitations for the issue creations and heavily restricted code contribution.

## Create an issue

Basically just follow the suggested templates:

* Bug report requires at least the way to reproduce the issue and behaviour description (expected and actual ones). In order to resolve the bug, the additional questions may be asked, please consider them as lesser evil.
* Feature requests basically just require feature description and the purpose why do you want this feature to be implemented. It is required to make sure that the feature you want is going to be implemented in the way you really want it (and to make sure that this feature is not already implemented).
* Questions and discussions have free templates, and you are free to ask your question in the way you want.

## Code contribution

There are some strict limitation for suggested pull requests:

* `autopep8`, `bandit`, `pylint`, `mypy` must pass.
* Test coverage must remain 100%.

### Code formatting

In order to resolve all difficult cases the `autopep8` is used. You can perform formatting at any time by running `make check` or running `autopep8` command directly.

### Code style

Again, the most checks can be performed by `make check` command, though some additional guidelines must be applied:

* Every class, every function (including private and protected), every attribute must be documented. The project follows [Google style documentation](https://google.github.io/styleguide/pyguide.html). The only exception is local functions.
* For any path interactions `pathlib.Path` must be used.
* Configuration interactions must go through `ahriman.core.configuration.Configuration` class instance.
* In case if class load requires some actions, it is recommended to create class method which can be used for class instantiating.
* The code must follow the exception safety, unless it is explicitly asked by end user. It means that most exceptions must be handled and printed to log, no other actions must be done (e.g. raising another exception).
* For the external command `ahriman.core.util.check_output` function must be used.
* Every temporary file/directory must be removed at the end of processing, no matter what. The ``tempfile`` module provides good ways to do it.
* Import order must be the following:

    ```python
    # optional imports from future module
    from __future__ import annotations

    # Module import for those which are installed into environment (no matter standard library or not)...
    import os
    # ...one per line...
    import pyalpm
    # ...in alphabetical order
    import sys

    # Blank line between
    # ``from module import submodule`` import
    from pathlib import Path
    # ...again in alphabet order. It is possible to do several imports, but make sure that they are also in alphabetical order.
    from pyalpm import Handle, Package

    # Blank line again and package imports
    from ahriman.core.configuration import Configuration
    ```

* One file should define only one class, exception is class satellites in case if file length remain less than 200 lines.
* It is possible to create file which contains some functions (e.g. `ahriman.core.util`), but in this case you would need to define `__all__` attribute.
* The file size mentioned above must be applicable in general. In case of big classes consider splitting them into traits.
* No global variable allowed outside of `ahriman.version` module.
* Single quotes are not allowed. The reason behind this restriction is the fact that docstrings must be written by using double quotes only, and we would like to make style consistent.
* If your class writes anything to log, the `ahriman.core.lazy_logging.LazyLogging` trait must be used.

### Other checks

The projects also uses typing checks (provided by `mypy`) and some linter checks provided by `pylint` and `bandit`. Those checks must be passed successfully for any open pull requests.
