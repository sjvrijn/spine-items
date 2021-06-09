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
Contains Data transformer's undo commands.

:author: A. Soininen (VTT)
:date:   25.5.2021
"""
from PySide2.QtWidgets import QUndoCommand


class InsertRow(QUndoCommand):
    """Inserts a row to value transformation model."""

    def __init__(self, message, model, row, data):
        """
        Args:
            message (str): undo message
            model (ValueTransformationsTableModel): model
            row (int): row index
            data (tuple): row data
            roles (Iterable of int): data roles
        """
        super().__init__(message)
        self._model = model
        self._row = row
        self._data = data

    def redo(self):
        self._model.insertRow(self._row)
        for column, (element, role) in enumerate(zip(self._data, self._model.SET_DATA_ROLES)):
            index = self._model.index(self._row, column)
            self._model.setData(index, element, role)

    def undo(self):
        self._model.removeRow(self._row)


class RemoveRow(QUndoCommand):
    """Removes a row from value transformation model."""

    def __init__(self, message, model, row):
        """
        Args:
            message (str): undo message
            model (ValueTransformationsTableModel): model
            row (int): row index
        """
        super().__init__(message)
        self._model = model
        self._row = row
        self._previous_data = tuple(model.index(row, col).data(role) for col, role in enumerate(model.GET_DATA_ROLES))

    def redo(self):
        self._model.removeRow(self._row)

    def undo(self):
        self._model.insertRow(self._row)
        for column, (element, role) in enumerate(zip(self._previous_data, self._model.SET_DATA_ROLES)):
            index = self._model.index(self._row, column)
            self._model.setData(index, element, role)


class AppendInstruction(QUndoCommand):
    """Appends an instruction to value transformation."""

    def __init__(self, editor, instruction):
        """
        Args:
            editor (InstructionsEditor): instructions editor

            instruction (dict): instruction to append
        """
        super().__init__("add instruction")
        self._editor = editor
        self._instruction = instruction

    def redo(self):
        self._editor.append_instruction(self._instruction)

    def undo(self):
        self._editor.pop_instruction(-1)


class RemoveInstruction(QUndoCommand):
    """Removes an instruction from value transformation."""

    def __init__(self, editor, row):
        """
        Args:
            editor (InstructionsEditor): instructions editor
            row (int): instruction row index
        """
        super().__init__("remove instruction")
        self._editor = editor
        self._row = row
        self._instruction = self._editor.instruction(self._row)

    def redo(self):
        self._editor.pop_instruction(self._row)

    def undo(self):
        self._editor.insert_instruction(self._row, self._instruction)


class ChangeOperation(QUndoCommand):
    """Changes instruction's operation."""

    def __init__(self, editor, row, operation):
        """
        Args:
            editor (InstructionsEditor): instructions editor
            row (int): instruction row index
            operation (str): operation's name
        """
        super().__init__("change operation")
        self._editor = editor
        self._row = row
        self._operation = operation
        self._previous_instruction = self._editor.instruction(self._row)

    def redo(self):
        self._editor.set_operation(self._row, self._operation)

    def undo(self):
        self._editor.set_instruction(self._row, self._previous_instruction)


class ChangeMultiplier(QUndoCommand):
    """Changes multiply operations multiplier."""

    def __init__(self, editor, row, multiplier):
        """
        Args:
            editor (InstructionsEditor): instructions editor
            row (int): instruction row index
            multiplier (float): operation's name
        """
        super().__init__("multiplier")
        self._editor = editor
        self._row = row
        self._previous_multiplier = self._editor.instruction(self._row)["rhs"]
        self._multiplier = multiplier
        if self._multiplier == self._previous_multiplier:
            self.setObsolete(True)

    def redo(self):
        self._editor.set_multiplier(self._row, self._multiplier)

    def undo(self):
        self._editor.set_multiplier(self._row, self._previous_multiplier)