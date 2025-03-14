# Contributing to ahriman

Welcome to ahriman! The goal of the project is to provide the best user experience to manage Arch linux repositories. In order to follow this we set some limitations for the issue creations and heavily restricted code contribution.

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

In order to resolve all difficult cases the `autopep8` is used. You can perform formatting at any time by running `tox` or running `autopep8` command directly.

### Code style

Again, the most checks can be performed by `tox` command, though some additional guidelines must be applied:

* Every class, every function (including private and protected), every attribute must be documented. The project follows [Google style documentation](https://google.github.io/styleguide/pyguide.html). The only exception is local functions.
* Correct way to document function (if a section is empty, e.g. no notes or there are no args, it should be omitted) is the following:

    ```python
    def foo(argument: str, *, flag: bool = False) -> int:
        """
        do foo. With very very very long
        docstring
  
        Notes:
            Very important note about this function
            Probably multi-line
  
        Args:
            argument(str): an argument. This argument has
                long description also
            flag(bool, optional): a flag (Default value = False)
  
        Returns:
            int: result with
            long description
  
        Raises:
            RuntimeError: a local function error occurs
  
        Examples:
            Very informative example how to use this function, e.g.::
  
                >>> foo("argument", flag=False)
  
            Note that function documentation is in rST.
        """
    ```
  
  `Returns` should be replaced with `Yields` for generators.

  Class attributes should be documented in the following way:

    ```python
    class Clazz(BaseClazz):
        """
        brand-new implementation of :class:`BaseClazz`
  
        Attributes:
            CLAZZ_ATTRIBUTE(int): (class attribute) a brand-new class attribute
            instance_attribute(str): an instance attribute
                with the long description
  
        Examples:
            Very informative class usage example, e.g.::
  
                >>> from module import Clazz
                >>> clazz = Clazz()
        """
  
        CLAZZ_ATTRIBUTE: ClassVar[int] = 42
  
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """
            Args:
                *args(Any): positional arguments
                **kwargs(Any): keyword arguments
            """
            self.instance_attribute = ""
    ```

  Note missing comment for the `__init__` method, which is the special case.

* Type annotations are the must, even for local functions. For the function argument `self` (for instance methods) and `cls` (for class methods) should not be annotated.
* For collection types built-in classes must be used if possible (e.g. `dict` instead of `typing.Dict`, `tuple` instead of `typing.Tuple`). In case if built-in type is not available, but `collections.abc` provides interface, it must be used (e.g. `collections.abc.Awaitable` instead of `typing.Awaitable`, `collections.abc.Iterable` instead of `typing.Iterable`). For union classes, the bar operator (`|`) must be used (e.g. `float | int` instead of `typing.Union[float, int]`), which also includes `typing.Optional` (e.g. `str | None` instead of `Optional[str]`).
* `classmethod` should (almost) always return `Self`. In case of mypy warning (e.g. if there is a branch in which function doesn't return the instance of `cls`) consider using `staticmethod` instead.
* Class attributes must be decorated as `ClassVar[...]`.
* Recommended order of function definitions in class:

    ```python
    class Clazz:
  
        def __init__(self) -> None: ...  # replace with `__post_init__` for dataclasses

        @property
        def property(self) -> Any: ...
  
        @cached_property
        def property_cached(self) -> Any: ...  # cached property has to be treated as normal one

        @classmethod
        def class_method(cls) -> Self: ...

        @staticmethod
        def static_method() -> Any: ...

        def __private_method(self) -> Any: ...

        def _protected_method(self) -> Any: ...

        def usual_method(self) -> Any: ...

        def __hash__(self) -> int: ...  # basically any magic (or look-alike) method
    ```
  
  Methods inside one group should be ordered alphabetically, the only exceptions are `__init__` (`__post_init__` for dataclasses), `__new__` and `__del__` methods which should be defined first. For test methods it is recommended to follow the order in which functions are defined.

  Though, we would like to highlight abstract methods (i.e. ones which raise `NotImplementedError`), we still keep in global order at the moment.

  For the most cases there is custom `pylint` plugin, which performs checks automatically.

* Abstract methods must raise `NotImplementedError` instead of using `abc.abstractmethod`. The reason behind this restriction is the fact that we have class/static abstract methods for those we need to define their attribute first making the code harder to read.
* For any path interactions `pathlib.Path` must be used.
* Configuration interactions must go through `ahriman.core.configuration.Configuration` class instance.
* In case if class load requires some actions, it is recommended to create class method which can be used for class instantiating.
* The most (expected) exceptions must be handled and printed to log, allowing service to continue work. However, fatal and (in some cases) unexpected exceptions may lead to the application termination.
* Exceptions without parameters should be raised without parentheses, e.g.:

    ```python
    raise RuntimeError
    ```

* For the external command `ahriman.core.util.check_output` function must be used.
* Every temporary file/directory must be removed at the end of processing, no matter what. The `tempfile` module provides good ways to do it.
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

* One file should define only one class, exception is class satellites in case if file length remains less than 400 lines.
* It is possible to create file which contains some functions (e.g. `ahriman.core.util`), but in this case you would need to define `__all__` attribute.
* The file size mentioned above must be applicable in general. In case of big classes consider splitting them into traits. Note, however, that `pylint` includes comments and docstrings into counter, thus you need to check file size by other tools.
* No global variable is allowed outside of `ahriman` module. `ahriman.core.context` is also special case.
* Single quotes are not allowed. The reason behind this restriction is the fact that docstrings must be written by using double quotes only, and we would like to make style consistent.
* If your class writes anything to log, the `ahriman.core.log.LazyLogging` trait must be used.
* Web API methods must be documented by using `aiohttp_apispec` library. The schema testing mostly should be implemented in related view class tests. Recommended example for documentation (excluding comments):

    ```python
    from marshmallow import Schema, fields  
    
    from ahriman.web.apispec.decorators import apidocs
    from ahriman.web.schemas import PackageNameSchema, PaginationSchema
    from ahriman.web.views.base import BaseView


    class RequestSchema(Schema):

        field = fields.String(metadata={"description": "Field description", "example": "foo"})


    class ResponseSchema(Schema):

        field = fields.String(required=True, metadata={"description": "Field description"})


    class Foo(BaseView):

        POST_PERMISSION = ...
        ROUTES = ...

        @apidocs(
            tags=["Tag"],
            summary="Do foo",
            description="Extended description of the method which does foo",
            error_400_enabled=True,  # exception raised by this method
            error_404_description="Repository is unknown",
            schema=ResponseSchema,  # leave empty if no responses here
            match_schema=PackageNameSchema,
            query_schema=PaginationSchema,
            body_schema=RequestSchema(many=True),
        )
        async def post(self) -> None: ...
    ```

* It is allowed to change web API to add new fields or remove optional ones. However, in case of model changes, new API version must be introduced.
* On the other hand, it is allowed to change method signatures, however, it is recommended to add new parameters as optional if possible. Deprecated API can be dropped during major release.
* Enumerations (`Enum` classes) are allowed and recommended. However, it is recommended to use `StrEnum` class if there are from/to string conversions and `IntEnum` otherwise.

### Other checks

The projects also uses typing checks (provided by `mypy`) and some linter checks provided by `pylint` and `bandit`. Those checks must be passed successfully for any open pull requests.

## Developers how to

### Run automated checks

```shell
tox
```

Must be usually done before any pushes.

### Generate documentation templates

```shell
tox -e docs
```

Must be usually done if there are changes in modules structure.

### Create release

```shell
tox -m release -- major.minor.patch
```

The command above will generate documentation, tags, etc., and will push them to GitHub. Other things will be handled by GitHub workflows automatically.

### Hotfixes policy

Sometimes it is required to publish hotfix with specific commits, but some features have been already committed, which should not be included to the hotfix. In this case, some manual steps are required:

1. Create new branch from the last stable release (`major.minor.patch`):

    ```shell
    git checkout -b release/major.minor major.minor.patch
    ```
   
2. Cherry-pick desired commit(s):

    ```shell
    git cherry-pick <commit-sha>
    ```
   
   Alternatively, make changes to the new branch and commit them.

3. Push newly created branch to remote:

    ```shell
    git push --set-upstream origin release/major.minor
    ```
   
4. Proceed to release as usual:

    ```shell
    tox -m release -- major.minor.patch+1
    ```
