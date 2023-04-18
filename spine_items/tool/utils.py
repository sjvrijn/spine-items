######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Utility functions for the Tool project item.

:author: A. Soininen (VTT)
:date:   1.4.2020
"""
from datetime import datetime
import glob
import os.path
from pathlib import Path
import re


def flatten_file_path_duplicates(file_paths, logger, log_duplicates=False):
    """Flattens the extra duplicate dimension in file_paths."""
    flattened = {}
    for required_file, paths in file_paths.items():
        if paths is not None:
            pick = paths[0]
            if len(paths) > 1 and log_duplicates:
                logger.msg_warning.emit(f"Multiple input files satisfy {required_file}; using {pick}")
            flattened[required_file] = pick
        else:
            flattened[required_file] = None
    return flattened


def file_paths_from_resources(resources):
    """
    Returns file paths from given resources.

    Args:
        resources (list): resources available

    Returns:
        a list of file paths, possibly including patterns
    """
    file_paths = []
    glob_chars = ("*", "?", "[")
    for resource in resources:
        if resource.hasfilepath:
            path = resource.path
            if any(char in path for char in glob_chars):
                file_paths += glob.glob(path)
            else:
                file_paths.append(path)
        elif resource.type_ == "file":
            file_paths.append(resource.label)
    return file_paths


def find_file(filename, resources):
    """
    Returns all occurrences of full paths to given file name in resources available.

    Args:
        filename (str): Searched file name (no path)
        resources (list): list of resources available from upstream items

    Returns:
        list: Full paths to file if found, None if not found
    """
    filename = os.path.normcase(filename)
    found_file_paths = []
    for file_path in file_paths_from_resources(resources):
        _, file_candidate = os.path.split(file_path)
        if os.path.normcase(file_candidate) == filename:
            found_file_paths.append(file_path)
    return found_file_paths if found_file_paths else None


def find_last_output_files(output_files, output_dir):
    """
    Returns latest output files.

    Args:
        output_files (list): output file patterns from tool specification
        output_dir (str): path to the execution output directory

    Returns:
        dict: a mapping from a file name pattern to the path of the most recent files in the results archive.
    """
    if not os.path.exists(output_dir):
        return {}
    recent_output_files = {}
    file_patterns = list(output_files)
    result = _find_last_output_dir(output_dir)
    if result is None:
        return {}
    full_archive_path = result[1]
    for pattern in list(file_patterns):
        full_path_pattern = os.path.join(full_archive_path, pattern)
        files_found = False
        for path in glob.glob(full_path_pattern):
            if os.path.exists(path):
                files_found = True
                file_list = recent_output_files.setdefault(pattern, [])
                file_list.append(os.path.normpath(path))
        if files_found:
            file_patterns.remove(pattern)
        if not file_patterns:
            return recent_output_files
    return recent_output_files


def _find_last_output_dir(output_dir, depth=0):
    """Searches for the latest output archive directory recursively.

    Args:
        output_dir (str):  path to the execution output directory
        depth (int): current recursion depth

    Returns:
        tuple: creation datetime and directory path
    """
    latest = None
    result_directory_pattern = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d.\d\d.\d\d")
    for path in Path(output_dir).iterdir():
        if not path.is_dir() or path.name == "failed":
            continue
        if result_directory_pattern.match(path.name) is not None:
            time_stamp = datetime.fromisoformat(path.name.replace(".", ":"))
            if latest is None or latest[0] < time_stamp:
                latest = (time_stamp, path)
        elif depth < 1:
            subdir_latest = _find_last_output_dir(str(path), depth + 1)
            if latest is None:
                latest = subdir_latest
            elif subdir_latest is not None and latest[0] < subdir_latest[0]:
                latest = subdir_latest
    return latest


def is_pattern(file_name):
    """Returns True if file_name is actually a file pattern."""
    return "*" in file_name or "?" in file_name


def make_dir_if_necessary(d, directory):
    """Creates a directory if given dictionary contains any items.

    Args:
        d (dict): Dictionary to check
        directory (str): Absolute path to directory that shall be created if necessary

    Returns:
        bool: True if directory was created successfully or dictionary is empty,
        False if creating the directory failed.
    """
    if len(d.items()) > 0:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError:
            return False
    return True
