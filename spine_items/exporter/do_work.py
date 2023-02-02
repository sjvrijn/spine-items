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
Exporter's execute kernel (do_work), as target for a multiprocess.Process

:authors: A. Soininen (VTT)
:date:    14.12.2020
"""
import os
from datetime import datetime
from pathlib import Path
from time import time

from spinedb_api.spine_io.exporters.writer import write, WriterException
from spinedb_api.spine_io.exporters.csv_writer import CsvWriter
from spinedb_api.spine_io.exporters.excel_writer import ExcelWriter
from spinedb_api.spine_io.exporters.gdx_writer import GdxWriter
from spinedb_api.spine_io.exporters.sql_writer import SqlWriter
from spinedb_api import DatabaseMapping, SpineDBAPIError
from spine_engine.utils.helpers import write_filter_id_file
from .specification import Specification, OutputFormat


def do_work(
    process,
    specification,
    output_time_stamps,
    cancel_on_error,
    gams_path,
    out_dir,
    databases,
    filter_id,
    filter_subdirectory,
    logger,
):
    """
    Exports databases using given specification as export mapping.

    Args:
        process (Process): unused
        specification (dict): export specification dictionary
        output_time_stamps (bool): if True, puts output files into time stamped subdirectories
        cancel_on_error (bool): if True, bails out on non-fatal errors
        gams_path (str): path to GAMS installation
        out_dir (str): base output directory
        databases (dict): databases to export
        filter_id (str): filter id
        filter_subdirectory (str): name of extra subdirectory used when filters have been applied
        logger (LoggerInterface): a logger

    Returns:
        tuple: boolean success flag, dictionary of output files
    """
    specification = Specification.from_dict(specification)
    successes = list()
    written_files = dict()
    for url, output_label in databases.items():
        output_file_name = _add_extension(output_label, specification.output_format)
        out_path = _subdirectory_for_fork(output_file_name, out_dir, output_time_stamps, filter_subdirectory)
        try:
            database_map = DatabaseMapping(url)
        except SpineDBAPIError as error:
            logger.msg_error.emit(f"Failed to export <b>{url}</b>: {error}")
            if cancel_on_error:
                return False, written_files
            successes.append(False)
            continue
        try:
            try:
                file = Path(out_path)
                file.parent.mkdir(parents=True, exist_ok=True)
                if file.exists():
                    file.unlink()
                writer = make_writer(specification.output_format, out_path, gams_path)
                specifications = specification.enabled_specifications().values()
                mappings = (m.root for m in specifications)
                header_always = (m.always_export_header for m in specifications)
                group_fns = (m.group_fn for m in specifications)
                write(database_map, writer, *mappings, empty_data_header=header_always, group_fns=group_fns)
            except (PermissionError, WriterException) as e:
                logger.msg_error.emit(str(e))
                if cancel_on_error:
                    return False, written_files
                successes.append(False)
            else:
                if isinstance(writer, CsvWriter):
                    files = writer.output_files()
                else:
                    files = {out_path}
                written_files[output_label] = files
                if len(files) > 1:
                    anchors = list()
                    for path in (Path(f) for f in files):
                        anchors.append(
                            f"\t<a style='color:#BB99FF;' title='{path}' href='file:///{path}'>{path.name}</a>"
                        )
                    logger.msg_success.emit(f"Wrote multiple files:<br>{'<br>'.join(anchors)}")
                else:
                    only_file = Path(next(iter(files)))
                    file_anchor = (
                        f"<a style='color:#BB99FF;' title='{only_file}' href='file:///{only_file}'>{only_file.name}</a>"
                    )
                    logger.msg_success.emit(f"Wrote {file_anchor}")
                if filter_id:
                    write_filter_id_file(filter_id, Path(out_path).parent)
                successes.append(True)
        finally:
            database_map.connection.close()
    return all(successes), written_files


def make_writer(output_format, out_path, gams_path):
    """
    Constructs a writer.

    Args:
        output_format (OutputFormat): output format
        out_path (str): path to output file
        gams_path (str): path to GAMS installation

    Returns:
        Writer: a writer
    """
    if output_format == OutputFormat.CSV:
        path = Path(out_path)
        return CsvWriter(path.parent, path.name)
    elif output_format == OutputFormat.EXCEL:
        return ExcelWriter(out_path)
    elif output_format == OutputFormat.SQL:
        return SqlWriter(out_path)
    return GdxWriter(out_path, gams_path)


_EXTENSIONS = {
    OutputFormat.CSV: ["csv", "dat", "txt"],
    OutputFormat.EXCEL: ["xlsx"],
    OutputFormat.SQL: ["sqlite", "sqlite3"],
    OutputFormat.GDX: ["gdx"],
}


def _add_extension(label, file_format):
    """Adds file format dependent extension to ``label`` if it is missing one.

    Args:
        label (str): label to add the extension to
        file_format (OutputFormat): file format

    Returns:
        str: file name
    """
    extensions = _EXTENSIONS[file_format]
    name, _, label_extension = label.rpartition(".")
    if name and label_extension.lower() in extensions:
        return label
    return label + "." + extensions[0]


def _subdirectory_for_fork(output_file_name, data_dir, output_time_stamps, filter_id_hash):
    """
    Creates scenario/tool based output directory for forked workflow.

    Args:
        output_file_name (str): file name
        data_dir (str): project item's data directory
        output_time_stamps (bool): True if time stamp data should be included in the output path
        filter_id_hash (str): hashed filter id

    Returns:
        str: absolute output path
    """
    if output_time_stamps:
        stamp = datetime.fromtimestamp(time())
        time_stamp = "run@" + stamp.isoformat(timespec="seconds").replace(":", ".")
    else:
        time_stamp = ""
    if filter_id_hash:
        if time_stamp:
            path = os.path.join(data_dir, filter_id_hash + "_" + time_stamp, output_file_name)
        else:
            path = os.path.join(data_dir, filter_id_hash, output_file_name)
    else:
        path = os.path.join(data_dir, time_stamp, output_file_name)
    return path
