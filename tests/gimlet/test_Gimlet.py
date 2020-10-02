######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for Gimlet project item.

:author: P. Savolainen (VTT)
:date:   25.5.2020
"""

import os
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtWidgets import QApplication
import spine_items.resources_icons_rc  # pylint: disable=unused-import
from spine_items.gimlet.item_info import ItemInfo
from spine_items.gimlet.gimlet import Gimlet
from spine_items.gimlet.gimlet_factory import GimletFactory
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestGimlet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = GimletFactory()
        item_dict = {
            "type": "Gimlet",
            "description": "",
            "use_shell": True,
            "shell_index": 0,
            "cmd": "",
            "selections": {},
            "work_dir_mode": True,
            "x": 0,
            "y": 0,
        }
        self.project = create_mock_project()
        self.gimlet = factory.make_item("G", item_dict, self.toolbox, self.project, self.toolbox)
        mock_finish_project_item_construction(factory, self.gimlet, self.toolbox)

    def test_item_type(self):
        self.assertEqual(Gimlet.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(Gimlet.item_category(), ItemInfo.item_category())

    def test_default_name_prefix(self):
        self.assertEqual(Gimlet.default_name_prefix(), "Gimlet")

    def test_notify_destination(self):
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. Files from <b>source name</b> are now available in <b>G</b>."
        )
        source_item.item_type = MagicMock(return_value="Importer")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Importer</b> and a <b>Gimlet</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Combiner")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. Files from <b>source name</b> are now available in <b>G</b>."
        )

        source_item.item_type = MagicMock(return_value="Data Store")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with("Link established")

        source_item.item_type = MagicMock(return_value="Data Transformer")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with("Link established")

        source_item.item_type = MagicMock(return_value="Exporter")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with("Link established")

        source_item.item_type = MagicMock(return_value="Tool")
        self.gimlet.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with("Link established")

    def test_rename(self):
        """Tests renaming a Gimlet."""
        self.gimlet.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        ret_val = self.gimlet.rename(expected_name)  # Do rename
        self.assertTrue(ret_val)
        self.assertEqual(expected_name, self.gimlet.name)  # Item name
        self.assertEqual(expected_name, self.gimlet._properties_ui.label_gimlet_name.text())  # Name label in props
        self.assertEqual(expected_name, self.gimlet.get_icon().name_item.text())  # Name item on Design View
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.gimlet.data_dir)  # Check data dir

    def test_split_gimlet_cmd(self):
        # Without expandable tags
        splitted = self.gimlet._split_gimlet_cmd("--input=data.dat -h 5")
        self.assertEqual(["--input=data.dat", "-h", "5"], splitted)
        splitted = self.gimlet._split_gimlet_cmd('--output="a long file name.txt"')
        self.assertEqual(["--output=a long file name.txt"], splitted)
        splitted = self.gimlet._split_gimlet_cmd("--file='file name with spaces.dat' -i 3")
        self.assertEqual(["--file=file name with spaces.dat", "-i", "3"], splitted)
        splitted = self.gimlet._split_gimlet_cmd("'quotation \"within\" a quotation'")
        self.assertEqual(['quotation "within" a quotation'], splitted)
        # With expandable tags
        splitted = self.gimlet._split_gimlet_cmd("@@optional_inputs@@")
        self.assertEqual(["@@optional_inputs@@"], splitted)
        splitted = self.gimlet._split_gimlet_cmd("@@url:database name with spaces@@")
        self.assertEqual(["@@url:database name with spaces@@"], splitted)
        splitted = self.gimlet._split_gimlet_cmd("@@url:spaced name@@ -a @@url:another spaced tag@@")
        self.assertEqual(["@@url:spaced name@@", "-a", "@@url:another spaced tag@@"], splitted)


if __name__ == "__main__":
    unittest.main()
