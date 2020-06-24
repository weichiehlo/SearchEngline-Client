# Created by Wei Chieh(Andy) Lo
# Date: 04/30/2019
# This is Fortinet confidential property
# Do NOT copy or modify script without permission by the author
# Contact: wlo@fortinet.com for support and questions
# Last updated: 04/30/2019 by Andy Lo

# Description: The purpose of this script is for testing ForiAP and Meru(GUI)
# 4/30/2019 Adding Meru testing in the Desktop Test Station and remove racks

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap

# Use by Pyinstall to refer files
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


# Styling for button, title and status bar
font_but = QtGui.QFont()
font_but.setFamily("Segoe UI Symbol")
font_but.setPointSize(15)
font_but.setWeight(95)

font_title = QtGui.QFont()
font_title.setFamily("Segoe UI Symbol")
font_title.setPointSize(20)
font_title.setWeight(95)

font_status = QtGui.QFont()
font_status.setFamily("Segoe UI Symbol")
font_status.setPointSize(10)
font_status.setWeight(95)

font_label = QtGui.QFont()
font_label.setFamily("Segoe UI Symbol")
font_label.setPointSize(8)
font_label.setWeight(95)


# PushButton class (Styling)
class PushBut(QtWidgets.QPushButton):

    def __init__(self, parent=None):
        super(PushBut, self).__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(0, 153, 0, 50%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid;"
                           "border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(251, 212, 220, 255);")

    def enterEvent(self, event):
        if self.isEnabled() is True:
            self.setStyleSheet("margin: 1px; padding: 7px;"
                               "background-color: rgba(0, 153, 0, 70%);"
                               "color: rgba(0, 0, 0, 255);"
                               "border-style: solid;border-radius: 3px;"
                               "border-width: 0.5px;"
                               "border-color: rgba(0, 230, 255, 255);")
        if self.isEnabled() is False:
            self.setStyleSheet("margin: 1px; padding: 7px;"
                               "background-color: rgba(0, 153, 0, 70%);"
                               "color: rgba(0, 0, 0, 255);"
                               "border-style: solid;"
                               "border-radius: 3px;border-width: 0.5px;"
                               "border-color: rgba(251, 212, 220, 255);")

    def leaveEvent(self, event):
        self.setStyleSheet("margin: 1px;"
                           " padding: 7px;"
                           "background-color: rgba(0, 153, 0, 50%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid"
                           ";border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(251, 212, 220, 255);")


# CheckBox class (Styling)
class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, parent=None):
        super(CheckBox, self).__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(128, 0, 0, 5%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid;"
                           "border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(50, 50, 50, 100%);")

# CheckBox class (Styling)
class TextBox(QtWidgets.QLineEdit):

    def __init__(self, placeholder):
        QtWidgets.QLineEdit.__init__(self)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(0, 0, 0, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid;"
                           "border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(50, 50, 50, 100%);")


# ComboBox class (Styling)
class ComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(0, 0, 0, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid;"
                           "border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(50, 50, 50, 100%);")


# LabelBox class (Styling)
class LabelBox(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(LabelBox, self).__init__(parent)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(15, 63, 140, 100%);"
                           "color: rgba(255, 255, 255, 100%);")


# LabelBox(for title) class (Styling)
class LabelBox_title(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(LabelBox_title, self).__init__(parent)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(29, 132, 196, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: inset;"
                           "border-radius: 3px;border-width: 5px;"
                           "border-color: rgba(159, 216, 237, 100%);")

# LabelBox(for status) class (Styling)
class LabelBox_status(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(LabelBox_status, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(102, 51, 0, 15%);"
                           "color: rgba(255, 255, 255, 100%);"
                           )

class LabelBox_Catogory(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(LabelBox_Catogory, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(74, 36, 156, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           )

# Tablr class (Styling)
class Table(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(QTableWidget, self).__init__(parent)
        self.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                           "color: rgba(255, 255, 255, 100%);")


# CheckBox class (Styling)
class DateBox(QtWidgets.QDateEdit):

    def __init__(self, parent=None):
        super(QDateEdit, self).__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("margin: 1px; padding: 7px;"
                           "background-color: rgba(0, 0, 0, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           "border-style: solid;"
                           "border-radius: 3px;border-width: 0.5px;"
                           "border-color: rgba(50, 50, 50, 100%);")