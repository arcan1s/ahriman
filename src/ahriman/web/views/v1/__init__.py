#
# Copyright (c) 2021-2023 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from ahriman.web.views.v1.service.add import AddView
from ahriman.web.views.v1.service.pgp import PGPView
from ahriman.web.views.v1.service.process import ProcessView
from ahriman.web.views.v1.service.rebuild import RebuildView
from ahriman.web.views.v1.service.remove import RemoveView
from ahriman.web.views.v1.service.request import RequestView
from ahriman.web.views.v1.service.search import SearchView
from ahriman.web.views.v1.service.update import UpdateView
from ahriman.web.views.v1.service.upload import UploadView

from ahriman.web.views.v1.status.logs import LogsView
from ahriman.web.views.v1.status.package import PackageView
from ahriman.web.views.v1.status.packages import PackagesView
from ahriman.web.views.v1.status.status import StatusView

from ahriman.web.views.v1.user.login import LoginView
from ahriman.web.views.v1.user.logout import LogoutView
