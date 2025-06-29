#
# Copyright (c) 2021-2025 ahriman team.
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
from ahriman.web.schemas.any_schema import AnySchema
from ahriman.web.schemas.aur_package_schema import AURPackageSchema
from ahriman.web.schemas.auth_schema import AuthSchema
from ahriman.web.schemas.build_options_schema import BuildOptionsSchema
from ahriman.web.schemas.changes_schema import ChangesSchema
from ahriman.web.schemas.counters_schema import CountersSchema
from ahriman.web.schemas.dependencies_schema import DependenciesSchema
from ahriman.web.schemas.error_schema import ErrorSchema
from ahriman.web.schemas.event_schema import EventSchema
from ahriman.web.schemas.event_search_schema import EventSearchSchema
from ahriman.web.schemas.file_schema import FileSchema
from ahriman.web.schemas.info_schema import InfoSchema
from ahriman.web.schemas.internal_status_schema import InternalStatusSchema
from ahriman.web.schemas.log_schema import LogSchema
from ahriman.web.schemas.login_schema import LoginSchema
from ahriman.web.schemas.logs_rotate_schema import LogsRotateSchema
from ahriman.web.schemas.logs_schema import LogsSchema
from ahriman.web.schemas.logs_search_schema import LogsSearchSchema
from ahriman.web.schemas.oauth2_schema import OAuth2Schema
from ahriman.web.schemas.package_name_schema import PackageNameSchema
from ahriman.web.schemas.package_names_schema import PackageNamesSchema
from ahriman.web.schemas.package_patch_schema import PackagePatchSchema
from ahriman.web.schemas.package_properties_schema import PackagePropertiesSchema
from ahriman.web.schemas.package_schema import PackageSchema
from ahriman.web.schemas.package_status_schema import PackageStatusSchema, PackageStatusSimplifiedSchema
from ahriman.web.schemas.package_version_schema import PackageVersionSchema
from ahriman.web.schemas.pagination_schema import PaginationSchema
from ahriman.web.schemas.patch_name_schema import PatchNameSchema
from ahriman.web.schemas.patch_schema import PatchSchema
from ahriman.web.schemas.pgp_key_id_schema import PGPKeyIdSchema
from ahriman.web.schemas.pgp_key_schema import PGPKeySchema
from ahriman.web.schemas.process_id_schema import ProcessIdSchema
from ahriman.web.schemas.process_schema import ProcessSchema
from ahriman.web.schemas.remote_schema import RemoteSchema
from ahriman.web.schemas.repository_id_schema import RepositoryIdSchema
from ahriman.web.schemas.repository_stats_schema import RepositoryStatsSchema
from ahriman.web.schemas.search_schema import SearchSchema
from ahriman.web.schemas.status_schema import StatusSchema
from ahriman.web.schemas.update_flags_schema import UpdateFlagsSchema
from ahriman.web.schemas.worker_schema import WorkerSchema
