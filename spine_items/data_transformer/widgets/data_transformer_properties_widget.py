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
Data transformer properties widget.

:author: A. Soininen
:date:   2.10.2020
"""
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from ..item_info import ItemInfo


class DataTransformerPropertiesWidget(QWidget):
    """Widget for the Data transformer item properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        from ..ui.data_transformer_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__()
        self.toolbox = toolbox
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.toolbox.ui.tabWidget_item_properties.addTab(self, ItemInfo.item_type())
        self.toolbox.specification_model_changed.connect(self._update_specification_model)

    @Slot()
    def _update_specification_model(self):
        model = self.toolbox.filtered_spec_factory_models[ItemInfo.item_type()]
        self.ui.specification_combo_box.setModel(model)
