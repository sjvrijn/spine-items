# -*- coding: utf-8 -*-
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

################################################################################
## Form generated from reading UI file 'value_type_filter_editor.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(354, 141)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.regexp_line_edit = QLineEdit(Form)
        self.regexp_line_edit.setObjectName(u"regexp_line_edit")

        self.verticalLayout.addWidget(self.regexp_line_edit)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setTextFormat(Qt.RichText)
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label_2.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.label_2)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setTextFormat(Qt.RichText)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.regexp_line_edit.setPlaceholderText(QCoreApplication.translate("Form", u"Type regular expression here...", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"<html><head/><body><p><a href=\"https://docs.python.org/3/library/re.html#regular-expression-syntax\"><span style=\" text-decoration: underline; color:#0000ff;\">Link</span></a> to regular expression syntax.</p></body></html>", None))
        self.label.setText(QCoreApplication.translate("Form", u"<html><head/><body><p>Available types for filtering:<br><span style=\" font-weight:600;\">single_value</span> - scalars, strings, booleans<br><span style=\" font-weight:600;\">array</span> - arrays<br><span style=\" font-weight:600;\">time_series</span> - time series<br><span style=\" font-weight:600;\">time_pattern</span> - time patterns<br><span style=\" font-weight:600;\">1d_map</span>, <span style=\" font-weight:600;\">2d_map</span>,... - maps of <span style=\" font-style:italic;\">n</span>d dimensions</p></body></html>", None))
    # retranslateUi

