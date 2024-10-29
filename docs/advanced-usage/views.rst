Writing own API endpoint
========================

The web service loads views dynamically, thus it is possible to add custom API endpoint or even web page. The views must be derived from ``ahriman.web.views.base.BaseView`` and implements HTTP methods. The API specification will be also loaded (if available), but optional. The implementation must be saved into the ``ahriman.web.views`` package

Let's consider example for API endpoint which always returns 204 with no response:

.. code-block:: python

   from aiohttp.web import Response, HTTPNoContent

   from ahriman.web.views.base import BaseView

   class PingView(BaseView):

       async def get(self) -> Response:
           # do nothing, just raise 204 response
           # check public methods of the BaseView class for all available controls
           raise HTTPNoContent

The ``get()`` method can be decorated by ``aiohttp_apispec`` methods, but we will leave it for self-study. Consider checking examples of usages in the main package.

In order to view to be set correctly to routes list, few more options are required to be set. First of all, it is required to specify ``ROUTES`` (list of strings), which contains list of all available routes, e.g.:

.. code-block:: python

   ...

       ROUTES = ["/api/v1/ping"]

In addition, it is also recommended to specify permission level for using this endpoint. Since this endpoint neither does anything nor returns sensitive information, it can be set to ``UserAccess.Unauthorized``:

.. code-block:: python

   ...

       GET_PERMISSION = UserAccess.Unauthorized

That's all. Just save the file as ``/usr/lib/python3.12/site-packages/ahriman/web/views/ping.py`` (replace ``python3.12`` with actual python version) and restart web server.

For more examples and details, please check builtin handlers and classes documentations.
