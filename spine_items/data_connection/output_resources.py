######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains utilities to scan for Data Connection's output resources.

:authors: A. Soininen (VTT)
:date:    4.12.2020
"""
from pathlib import Path
from spine_engine.project_item.project_item_resource import file_resource, transient_file_resource
from spine_engine.utils.serialization import path_in_dir


def scan_for_resources(provider, files, project_dir):
    """
    Creates file resources based on DC files.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        files (list of str): path to fata files
        project_dir (str): absolute path to project directory

    Returns:
        list of ProjectItemResource: output resources
    """
    resources = list()
    for ref in files:
        if path_in_dir(ref, provider.data_dir):
            resource = file_resource(
                provider.name, ref, label=f"<{provider.name}>/" + Path(ref).relative_to(provider.data_dir).as_posix()
            )
        elif path_in_dir(ref, project_dir):
            path = Path(ref)
            label = "<project>/" + Path(ref).relative_to(project_dir).as_posix()
            if path.exists():
                resource = file_resource(provider.name, ref, label=label)
            else:
                resource = transient_file_resource(provider.name, label)
        else:
            if Path(ref).exists():
                resource = file_resource(provider.name, ref)
            else:
                resource = transient_file_resource(provider.name, ref)
        resources.append(resource)
    return resources
