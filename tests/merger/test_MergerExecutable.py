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
Unit tests for MergerExecutable.

:author: A. Soininen
:date:   6.4.2020
"""
from multiprocessing import Lock
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spinedb_api import create_new_spine_database, DatabaseMapping, import_functions
from spinedb_api.spine_db_server import db_server_manager
from spine_engine.project_item.project_item_resource import database_resource
from spine_engine.project_item.connection import Connection
from spine_engine.spine_engine import SpineEngine, SpineEngineState
from spine_items.merger.executable_item import ExecutableItem
from spine_items.data_store.executable_item import ExecutableItem as DSExecutableItem
from spine_items.utils import convert_to_sqlalchemy_url


class TestMergerExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Merger")

    def test_from_dict(self):
        name = "Output Data Store"
        item_dict = {"type": "Data Store", "description": "", "x": 0, "y": 0, "cancel_on_error": True}
        logger = mock.MagicMock()
        item = ExecutableItem.from_dict(
            item_dict, name, self._temp_dir.name, None, {}, logger
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Merger", item.item_type())

    def test_stop_execution(self):
        executable = ExecutableItem("name", True, self._temp_dir.name, mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute(self):
        executable = ExecutableItem("name", True, self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_execute_merge_two_dbs(self):
        """Creates two db's with some data and merges them to a third db."""
        db1_path = Path(self._temp_dir.name, "db1.sqlite")
        db1_url = f"sqlite:///{str(db1_path)}"
        # Add some data to db1
        db1_map = DatabaseMapping(db1_url, create=True)
        import_functions.import_object_classes(db1_map, ["a"])
        import_functions.import_objects(db1_map, [("a", "a_1")])
        # Commit to db1
        db1_map.commit_session("Add an object class 'a' and an object for unit tests.")
        db2_path = Path(self._temp_dir.name, "db2.sqlite")
        db2_url = f"sqlite:///{str(db2_path)}"
        # Add some data to db2
        db2_map = DatabaseMapping(db2_url, create=True)
        import_functions.import_object_classes(db2_map, ["b"])
        import_functions.import_objects(db2_map, [("b", "b_1")])
        # Commit to db2
        db2_map.commit_session("Add an object class 'b' and an object for unit tests.")
        # Close connections
        db1_map.connection.close()
        db2_map.connection.close()
        # Make an empty output db
        db3_path = Path(self._temp_dir.name, "db3.sqlite")
        db3_url = f"sqlite:///{str(db3_path)}"
        create_new_spine_database(db3_url)
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        executable = ExecutableItem("name", True, self._temp_dir.name, logger)
        input_db_resources = [database_resource("provider", db1_url), database_resource("provider", db2_url)]
        output_db_resources = [database_resource("receiver", db3_url)]
        with db_server_manager() as mngr_queue:
            for r in input_db_resources + output_db_resources:
                r.metadata["db_server_manager_queue"] = mngr_queue
            self.assertTrue(executable.execute(input_db_resources, output_db_resources, Lock()))
        # Check output db
        output_db_map = DatabaseMapping(db3_url)
        class_list = output_db_map.object_class_list().all()
        self.assertEqual(len(class_list), 2)
        self.assertEqual(class_list[0].name, "a")
        self.assertEqual(class_list[1].name, "b")
        object_list_a = output_db_map.object_list(class_id=class_list[0].id).all()
        self.assertEqual(len(object_list_a), 1)
        self.assertEqual(object_list_a[0].name, "a_1")
        object_list_b = output_db_map.object_list(class_id=class_list[1].id).all()
        self.assertEqual(len(object_list_b), 1)
        self.assertEqual(object_list_b[0].name, "b_1")
        output_db_map.connection.close()

    def test_write_order(self):
        db1_path = Path(self._temp_dir.name, "db1.sqlite")
        db1_url = f"sqlite:///{str(db1_path)}"
        # Add some data to db1
        db1_map = DatabaseMapping(db1_url, create=True)
        import_functions.import_data(db1_map, object_classes=["fish"])
        # Commit to db1
        db1_map.commit_session("Add test data.")
        db2_path = Path(self._temp_dir.name, "db2.sqlite")
        db2_url = f"sqlite:///{str(db2_path)}"
        # Add some data to db2
        db2_map = DatabaseMapping(db2_url, create=True)
        import_functions.import_data(db2_map, object_classes=["cat"])
        # Commit to db2
        db2_map.commit_session("Add test data.")
        # Close connections
        db1_map.connection.close()
        db2_map.connection.close()
        # Make an empty output db
        db3_path = Path(self._temp_dir.name, "db3.sqlite")
        db3_url = f"sqlite:///{str(db3_path)}"
        # Make two mergers
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        merger1 = ExecutableItem("merger1", True, self._temp_dir.name, logger)
        merger2 = ExecutableItem("merger2", True, self._temp_dir.name, logger)
        # Make two input DS and one output DS
        input_ds1 = DSExecutableItem(
            "ds1",
            convert_to_sqlalchemy_url({"dialect": "sqlite", "database": str(db1_path)}),
            self._temp_dir.name,
            logger,
        )
        input_ds2 = DSExecutableItem(
            "ds2",
            convert_to_sqlalchemy_url({"dialect": "sqlite", "database": str(db2_path)}),
            self._temp_dir.name,
            logger,
        )
        output_ds = DSExecutableItem(
            "output_ds",
            convert_to_sqlalchemy_url({"dialect": "sqlite", "database": str(db3_path)}),
            self._temp_dir.name,
            logger,
        )
        # Make connections
        conn1in = Connection("ds1", "right", "merger1", "left")
        conn2in = Connection("ds2", "right", "merger2", "left")
        conn1out = Connection("merger1", "left", "output_ds", "right", options={"write_index": 2})
        conn2out = Connection("merger2", "left", "output_ds", "right", options={"write_index": 1})
        # Make and run engine
        items = {x.name: x for x in (merger1, merger2, input_ds1, input_ds2, output_ds)}
        execution_permits = {name: True for name in items}
        # We can't easily enforce merger1 to execute before merger2 so the write index matters...
        # So for the moment, let's run 5 times and hope
        for _ in range(5):
            engine = SpineEngine(
                items=items,
                connections=[x.to_dict() for x in (conn1in, conn2in, conn1out, conn2out)],
                execution_permits=execution_permits,
            )
            engine.make_item = lambda item_name, direction: items[item_name]
            create_new_spine_database(db3_url)
            engine.run()
            self.assertEqual(engine.state(), SpineEngineState.COMPLETED)
            db3_map = DatabaseMapping(db3_url, create=True)
            commits = db3_map.query(db3_map.commit_sq).all()
            merger1_idx = next(iter(k for k, commit in enumerate(commits) if db1_url in commit.comment))
            merger2_idx = next(iter(k for k, commit in enumerate(commits) if db2_url in commit.comment))
            self.assertTrue(merger2_idx < merger1_idx)
            db3_map.connection.close()


if __name__ == "__main__":
    unittest.main()
