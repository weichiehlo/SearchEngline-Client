# Created by Wei Chieh(Andy) Lo
# Date: 06/20/2019
# This is Fortinet confidential property
# Do NOT copy or modify script without permission by the author
# Contact: wlo@fortinet.com for support and questions
# Last updated: 06/20/2019 by Andy Lo

# Description: The purpose of this script is for Parsing data and log them into database

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
import os, subprocess
from styling import *
import backend_database
from dataScraper import DataBaseInfo
import datetime, sys
from graph import graphFigure
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging
import csv
import re

from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from time import gmtime, strftime




# Use by Pyinstall to refer files
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# Global variable for the test command
logfile = ""
start_time = 0
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='Progess.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S', level=logging.INFO)



# BlackList Keywords



class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(resource_path("Logo1.png")))
        self.title = 'Production Search/Analyzer Engine'
        # self.x = 300
        # self.y = 300
        # self.width = 1100
        # self.height = 500
        self.setWindowTitle(self.title)
        self.screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.setGeometry(self.screen.width() / 8, 50, 600, 400)
        self.setMinimumSize(0, 0)
        #self.setGeometry(self.x, self.y, self.width, self.height)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100%);"
                           "color: rgba(255, 255, 255, 100%);"
                           )
        QMessageBox.about(self, "ReadMe", "This is Fortinet confidential property \n "
                                          "Do NOT copy or modify script without permission by the author "
                                          "\n Contact: wlo@fortinet.com for support and questions")

        self.table_widget = SeachEngine_App(self)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn);
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        self.scroll.setWidget(self.table_widget)
        self.scroll.setWidgetResizable(True)

        self.setCentralWidget(self.scroll)

        #
        # self.setCentralWidget(self.table_widget)


        self.show()

# Warning message when closing the app
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Close Message',
                                     "Are You Sure You Want To Quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class SeachEngine_App(QWidget):
    # signal declaration
    tab1_sig = pyqtSignal(dict)
    tab5_sig = pyqtSignal(dict)
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        stylesheet = """ 
            QTabBar::tab:selected {background: rgb(150,150,150);}
            QTabBar::tab:unselected {color: rgb(0,0,0);}
            QTabWidget>QWidget>QWidget{background: black;}
            """
        self.setStyleSheet(stylesheet)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        #self.tabs.resize(600, 200)




        # Add tabs
        self.tabs.addTab(self.tab1, "Database Restore")
        self.tabs.addTab(self.tab2, "Production Log Analyzer Engine")
        self.tabs.addTab(self.tab3, "Production Log Sensor Graphical Table Interface")
        self.tabs.addTab(self.tab4, "Production Log Error List Graphical Interface")
        self.tabs.addTab(self.tab5, "Production Log Sensor VS Graphical Interface (Scattered)")
        self.tabs.addTab(self.tab6, "Production Log Sensor VS Graphical Interface (Horizontal)")






        # Thread declaration
        self.app_thread = Qapp_thread()

        # Styling for the title
        self.title = LabelBox_title("Search Engine")
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(font_title)

        # Styling for the start button
        self.startbutton = PushBut(self)
        self.startbutton.setText("Create DataBase ⯈")
        self.startbutton.setFont(font_but)


        # Declare TextBox Widgets
        self.filepath_box = TextBox(self)
        self.filepath_box.setText("C:\\Users\\wlo\\Desktop\\Wistron\\IQC")

        # Declare Label Box for filepath
        self.filepath_label = LabelBox("Please Enter the Log Directory (.tgz)")
        self.filepath_label.setFont(font_label)



        # Declare Label Box for status with styling
        self.status = LabelBox_status("Ready")
        self.status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                  "color: rgba(255, 255, 255, 100%);"
                                  )
        self.status.setFont(font_status)
        self.status.setAlignment(Qt.AlignCenter)


        # Declare output box
        self.text_edit_widget = QPlainTextEdit()
        self.text_edit_widget.setReadOnly(True)


        # Declare a image as a label
        self.imageLabel = QLabel(self)
        self.pixmap = QPixmap(resource_path('F.PNG'))
        self.imageLabel.setPixmap(self.pixmap)

        self.tab2_imageLabel = QLabel(self)
        self.tab2_imageLabel.setPixmap(self.pixmap)

        self.tab3_imageLabel = QLabel(self)
        self.tab3_imageLabel.setPixmap(self.pixmap)

        self.tab4_imageLabel = QLabel(self)
        self.tab4_imageLabel.setPixmap(self.pixmap)

        self.tab5_imageLabel = QLabel(self)
        self.tab5_imageLabel.setPixmap(self.pixmap)

        self.tab6_imageLabel = QLabel(self)
        self.tab6_imageLabel.setPixmap(self.pixmap)




        self.tab1_model_text_label = LabelBox("Please Enter The Model (First 6 Letters of SN)")
        self.tab1_model_text_label.setFont(font_label)
        self.tab1_model_text = TextBox(self)
        self.tab1_model_text.setText('FG100F')

        self.tab1_table_1_text_label = LabelBox("Please Enter The Name of The Table")
        self.tab1_table_1_text_label.setFont(font_label)
        self.tab1_table_1_text = TextBox(self)

        self.tab1_test_type_text_label = LabelBox("Please Enter Test Type [Seperate by ,]")
        self.tab1_test_type_text_label.setFont(font_label)
        self.tab1_test_type_text = TextBox(self)
        self.tab1_test_type_text.setToolTip("ITS,SFC,HTS")
        self.tab1_test_type_text.setText('ITS')

        self.tab1_checkBox = CheckBox("Manuel Logs?")

        self.tab1_reg_text_label = LabelBox("Please Enter The Regex")
        self.tab1_reg_text_label.setFont(font_label)
        self.tab1_reg_text = TextBox(self)
        self.tab1_reg_text.setToolTip("Please use ?P<alarm> tag and ?P<reading> for alarm and sensor reading and \"\" for ,")
        self.tab1_reg_text.setText("Sensor name\s+alarm=(?P<alarm>\d)(?:\s+value=(?P<reading>(?:(\d+\.\d+|\d+))|)|)")

        self.tab1_base_text_label = LabelBox("Please Enter The Base Command")
        self.tab1_base_text_label.setFont(font_label)
        self.tab1_base_text = TextBox(self)

        self.tab1_from_select_label = LabelBox("Please Select The Range (From)")
        self.tab1_from_select_label.setFont(font_label)

        self.tab1_to_select_label = LabelBox("Please Select The Range (to)")
        self.tab1_to_select_label.setFont(font_label)

        self.tab1_export_csv_button = PushBut(self)
        self.tab1_export_csv_button.setText("Save Parsing Info to CSV")
        self.tab1_export_csv_button.setFont(font_but)

        self.tab1_ReferenceBuffer_label = LabelBox("Please Enter The Reference Buffer")
        self.tab1_ReferenceBuffer_label.setFont(font_label)
        self.tab1_ReferenceBuffer = TextBox(self)

        self.tab1_Unit_label = LabelBox("Please Enter The Unit")
        self.tab1_Unit_label.setFont(font_label)
        self.tab1_Unit = TextBox(self)
        self.tab1_log_condition_label = LabelBox("Please Select the Log Condition")
        self.tab1_log_condition_label.setFont(font_label)
        self.tab1_log_condition_dropdown = ComboBox()
        self.tab1_log_condition_dropdown.addItems(['ALL', 'PASS', 'FAIL'])





        self.tab1_from_select = DateBox(self)
        self.tab1_to_select = DateBox(self)
        self.tab1_from_select.setDate(QDate(1999, 1, 1))
        self.tab1_to_select.setDate(QDate.currentDate())

        # Declare Label Box for filepath
        self.tab1_sqlpath_label = LabelBox("Please Select the SQL file to Restore")
        self.tab1_sqlpath_label.setFont(font_label)

        self.tab1_cur_sqlpath = LabelBox_status("Empty")
        self.tab1_cur_sqlpath.setStyleSheet("background-color: rgba(0, 0, 0, 100%);"
                                  "color: rgba(255, 255, 255, 100%);"
                                  )
        self.tab1_cur_sqlpath.setFont(font_status)
        self.tab1_cur_sqlpath.setAlignment(Qt.AlignCenter)
        self.tab1_sqlpath_button = PushBut(self)
        self.tab1_sqlpath_button.setText("Select File(.sql)")
        self.tab1_restore_button = PushBut(self)
        self.tab1_restore_button.setText("Restore Data Base")
        self.tab1_restore_button.setFont(font_but)

        self.tab1_csv_section = LabelBox_Catogory("Add Parsing Info to CSV Section")
        self.tab1_csv_section.setFont(font_status)
        self.tab1_csv_section.setAlignment(Qt.AlignCenter)
        self.tab1_create_section = LabelBox_Catogory("Create DataBase Section")
        self.tab1_create_section.setFont(font_status)
        self.tab1_create_section.setAlignment(Qt.AlignCenter)
        self.tab1_restore_section = LabelBox_Catogory("Restore DataBase Section")
        self.tab1_restore_section.setFont(font_status)
        self.tab1_restore_section.setAlignment(Qt.AlignCenter)





        # database declaration Dummy data base, will update with update db function

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname="")

        # Declare grid styling for the app
        self.tab1.layout = QtWidgets.QGridLayout()
        self.tab2.layout = QtWidgets.QGridLayout()
        self.tab3.layout = QtWidgets.QGridLayout()
        self.tab4.layout = QtWidgets.QGridLayout()
        self.tab5.layout = QtWidgets.QGridLayout()
        self.tab6.layout = QtWidgets.QGridLayout()



        # Put the rest of widgets into grid
        self.tab1.layout.addWidget(self.imageLabel, 0, 0, 1, 3)
        self.tab1.layout.addWidget(self.title, 1, 0, 4, 3)
        # self.tab1.layout.addWidget(self.tab1_csv_section, 5, 0, 2, 3)
        # self.tab1.layout.addWidget(self.tab1_table_1_text_label, 9, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_table_1_text, 9, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_reg_text_label, 10, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_reg_text, 10, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_base_text_label, 11, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_base_text, 11, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_ReferenceBuffer_label, 12, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_ReferenceBuffer, 12, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_Unit_label, 13, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_Unit, 13, 1, 1, 1)
        #
        # self.tab1.layout.addWidget(self.tab1_log_condition_label, 14, 0, 1, 1)
        #
        #
        # self.tab1.layout.addWidget(self.tab1_log_condition_dropdown, 14, 1, 1, 1)
        #
        # self.tab1.layout.addWidget(self.tab1_export_csv_button, 15, 0, 1, 4)
        # self.tab1.layout.addWidget(self.tab1_create_section, 16, 0, 2, 3)
        #
        # self.tab1.layout.addWidget(self.tab1_model_text_label, 18, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_model_text, 18, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_test_type_text_label, 19, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_test_type_text, 19, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_from_select_label, 20, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_from_select, 20, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_to_select_label, 21, 0, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_to_select, 21, 1, 1, 1)
        # self.tab1.layout.addWidget(self.filepath_label, 22, 0, 1, 1)
        # self.tab1.layout.addWidget(self.filepath_box, 22, 1, 1, 1)
        # self.tab1.layout.addWidget(self.tab1_checkBox, 23, 1, 1, 1)
        # self.tab1.layout.addWidget(self.startbutton, 24, 0, 2, 4)

        self.tab1.layout.addWidget(self.tab1_restore_section, 28, 0, 2, 3)
        self.tab1.layout.addWidget(self.tab1_sqlpath_label, 31, 0, 1, 1)
        self.tab1.layout.addWidget(self.tab1_sqlpath_button, 31, 1, 1, 1)
        self.tab1.layout.addWidget(self.tab1_cur_sqlpath, 32, 0, 1, 3)
        self.tab1.layout.addWidget(self.tab1_restore_button, 33, 0, 1, 3)


        self.tab1.layout.addWidget(self.text_edit_widget, 36, 0, 5, 3)
        self.tab1.layout.addWidget(self.status, 40, 0, 3, 3)





        # Set app_grid as the layout
        self.tab1.setLayout(self.tab1.layout)


        # Actions
        # Action when clicking the start button
        self.startbutton.clicked.connect(self.start_button)
        self.tab1_export_csv_button.clicked.connect(self.save_parsing_info)
        self.tab1_sqlpath_button.clicked.connect(self.select_sql_action)
        self.tab1_restore_button.clicked.connect(self.restore_db_action)








        #TAB 2 STARTS HERE

        #Declare a table in tab 2
        self.tab2_tableWidget = Table(self)
        self.tab2_tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tab2_tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tab2_tableWidget.resizeColumnsToContents()
        stylesheet = "::section{Background-color:rgb(50,50,50);border-radius:14px;color:rgb(255,255,255);}"
        self.tab2_tableWidget.horizontalHeader().setStyleSheet(stylesheet)
        self.tab2_tableWidget.verticalHeader().setStyleSheet(stylesheet)

        self.tab2_view_table_button = PushBut(self)
        self.tab2_view_table_button.setText("⯈ View Customized Table")
        self.tab2_view_table_button.setFont(font_but)

        self.tab2_create_button = PushBut(self)
        self.tab2_create_button.setText("↯ Save Customized Table")
        self.tab2_create_button.setFont(font_but)

        self.tab2_show_button = PushBut(self)
        self.tab2_show_button.setText("⯈ Show Saved Customized Table")
        self.tab2_show_button.setFont(font_but)

        self.tab2_model_select_label = LabelBox("Please Select The Model")
        self.tab2_model_select_label.setFont(font_label)

        self.tab2_table_1_select_label = LabelBox("Please Select The Table")
        self.tab2_table_1_select_label.setFont(font_label)

        self.tab2_test_type_select_label = LabelBox("Please Select Test Type")
        self.tab2_test_type_select_label.setFont(font_label)

        self.tab2_model_select = ComboBox()

        self.tab2_table_1_select = ComboBox()

        self.tab2_test_type_select = ComboBox()

        self.tab2_sn_low = TextBox(self)
        #self.tab2_sn_low.setText("FG3H0E3917903218")
        self.tab2_sn_low.setPlaceholderText("Please Enter Start SN.")

        self.tab2_sn_high = TextBox(self)
        #self.tab2_sn_high.setText("FG3H0E3917903220")
        self.tab2_sn_high.setPlaceholderText("Please Enter End SN.")

        self.tab2_sn_low_label = LabelBox("Enter Low SN")
        self.tab2_sn_low_label.setFont(font_label)

        self.tab2_sn_high_label = LabelBox("Enter High SN")
        self.tab2_sn_high_label.setFont(font_label)

        self.tab2_status = LabelBox_status("Ready")
        self.tab2_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                  "color: rgba(255, 255, 255, 100%);"
                                  )
        self.tab2_status.setFont(font_status)
        self.tab2_status.setAlignment(Qt.AlignCenter)

        self.tab2_custom_view_select_label = LabelBox("Please Select the Customized Table")
        self.tab2_custom_view_select_label.setFont(font_label)
        self.tab2_custom_view_select = ComboBox()

        # Styling for the title
        self.tab2_title = LabelBox_title("Analyzer Engine")
        self.tab2_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab2_title.setAlignment(Qt.AlignCenter)
        self.tab2_title.setFont(font_title)

        self.tab2_from_select_label = LabelBox("Please Select The Range (From)")
        self.tab2_from_select_label.setFont(font_label)

        self.tab2_to_select_label = LabelBox("Please Select The Range (to)")
        self.tab2_to_select_label.setFont(font_label)

        self.tab2_from_select = DateBox(self)
        self.tab2_to_select = DateBox(self)


        self.tab2_save_view_label = LabelBox("Table Name (to Save)")
        self.tab2_save_view_label.setFont(font_label)
        self.tab2_save_view_txt = TextBox(self)
        self.tab2_save_view_txt.setPlaceholderText("Please Enter the Name of the View")

        self.tab2_graph_label = LabelBox("Graph(Limits and Intervals)")
        self.tab2_graph_label.setFont(font_label)

        self.tab2_graph_low_limit_txt = TextBox(self)
        self.tab2_graph_low_limit_txt.setPlaceholderText("Low Limit")


        self.tab2_graph_high_limit_txt = TextBox(self)
        self.tab2_graph_high_limit_txt.setPlaceholderText("High Limit")

        self.tab2_graph_interval_txt = TextBox(self)
        self.tab2_graph_interval_txt.setPlaceholderText("Interval")

        self.tab2_max_checkBox = CheckBox("Per SN MAX Value?")
        self.tab2_avg_checkBox = CheckBox("Per SN AVG Value?")




        self.tab2.layout.addWidget(self.tab2_imageLabel, 0, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_title, 1, 0, 4, 6)
        self.tab2.layout.addWidget(self.tab2_model_select_label, 5, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_model_select, 5, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_table_1_select_label, 6, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_table_1_select, 6, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_test_type_select_label, 8, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_test_type_select, 8, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_sn_low_label, 9, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_sn_low, 9, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_sn_high_label, 10, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_sn_high, 10, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_from_select_label, 11, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_to_select_label, 12, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_from_select, 11, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_to_select, 12, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_graph_label, 13, 0, 1, 1)
        self.tab2.layout.addWidget(self.tab2_graph_low_limit_txt, 13, 1, 1, 1)
        self.tab2.layout.addWidget(self.tab2_graph_high_limit_txt, 13, 2, 1, 1)
        self.tab2.layout.addWidget(self.tab2_graph_interval_txt, 13, 3, 1, 1)

        self.tab2.layout.addWidget(self.tab2_save_view_label, 14, 0, 1, 1)
        self.tab2.layout.addWidget(self.tab2_save_view_txt, 14, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_max_checkBox, 15, 1, 1, 1)
        self.tab2.layout.addWidget(self.tab2_avg_checkBox, 15, 2, 1, 1)
        self.tab2.layout.addWidget(self.tab2_view_table_button, 16, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_create_button, 17, 0, 1, 6)



        self.tab2.layout.addWidget(self.tab2_status, 20, 0, 1, 6)
        self.tab2.layout.addWidget(self.tab2_tableWidget, 24, 0, 5, 7)
        self.tab2.layout.addWidget(self.tab2_custom_view_select_label, 23, 0, 1, 1)
        self.tab2.layout.addWidget(self.tab2_custom_view_select, 23, 1, 1, 6)
        self.tab2.layout.addWidget(self.tab2_show_button, 34, 0, 1, 6)
        self.tab2.setLayout(self.tab2.layout)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.tab2_create_button.clicked.connect(self.tab2_create_view)
        self.tab2_show_button.clicked.connect(self.tab2_show_view)
        self.tab2_view_table_button.clicked.connect(self.tab2_preview_view)


        db_table = []
        try:
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        except TypeError as e:
            print("No data tab2")
        self.tab2_model_select.clear()
        self.tab2_model_select.addItems(db_table)

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab2_model_select.currentText())
        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
        db_table.sort()
        self.tab2_table_1_select.clear()
        self.tab2_table_1_select.addItems(db_table)
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab2_test_type_select.clear()
        self.tab2_test_type_select.addItems(test_type_list)
        self.tab2_custom_view_select.clear()
        self.tab2_custom_view_select.addItems(self.dbms.return_list_of_views())

        try:
            self.tab2_graph_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab2_table_1_select.currentText(),self.tab2_model_select.currentText(),self.tab2_test_type_select.currentText()))
            self.tab2_graph_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab2_table_1_select.currentText(),self.tab2_model_select.currentText(),self.tab2_test_type_select.currentText()))
        except:
            pass

        self.tab2_model_select.currentTextChanged.connect(self.tab2_on_model_changed)
        self.tab2_table_1_select.currentTextChanged.connect(self.tab2_on_sensor_table_changed)
        self.tab2_test_type_select.currentTextChanged.connect(self.tab2_on_sensor_table_changed)

        self.tab2_from_select.setDate(QDate(1999, 1, 1))
        self.tab2_to_select.setDate(QDate.currentDate())

        self.tab2_max_checkBox.stateChanged.connect(self.onStateChange)
        self.tab2_avg_checkBox.stateChanged.connect(self.onStateChange)

#tab3

        self.tab3_title = LabelBox_title("Sensor List Graphical Interface")
        self.tab3_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab3_title.setAlignment(Qt.AlignCenter)
        self.tab3_title.setFont(font_title)

        self.tab3_sensor_graph_button = PushBut(self)
        self.tab3_sensor_graph_button.setText("Bar Graph")
        self.tab3_sensor_graph_button.setFont(font_but)

        self.tab3_sensor_line_graph_button = PushBut(self)
        self.tab3_sensor_line_graph_button.setText("Line Graph")
        self.tab3_sensor_line_graph_button.setFont(font_but)

        self.tab3_sensor_export_button = PushBut(self)
        self.tab3_sensor_export_button.setText("Export")
        self.tab3_sensor_export_button.setFont(font_but)


        self.tab3_sensor_graph_add_button = PushBut(self)
        self.tab3_sensor_graph_add_button.setText("Add to Graph")
        self.tab3_sensor_graph_add_button.setFont(font_but)

        self.tab3_sensor_graph_remove_button = PushBut(self)
        self.tab3_sensor_graph_remove_button.setText("Remove from Graph")
        self.tab3_sensor_graph_remove_button.setFont(font_but)

        self.tab3_sensor_graph_clear_button = PushBut(self)
        self.tab3_sensor_graph_clear_button.setText("Clear All Graph")
        self.tab3_sensor_graph_clear_button.setFont(font_but)

        self.tab3_sensor_select_label = LabelBox("Please Select the Sensor to Add to the Bar Graph")
        self.tab3_sensor_select_label.setFont(font_label)
        self.tab3_sensor_select = ComboBox()

        self.tab3_db_select_label = LabelBox("Please Select the DataBase")
        self.tab3_db_select_label.setFont(font_label)
        self.tab3_db_select = ComboBox()

        self.tab3_text_edit_widget = QPlainTextEdit()
        self.tab3_text_edit_widget.setReadOnly(True)

        self.tab3_status = LabelBox_status("Table to Be Displayed")
        self.tab3_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                       "color: rgba(255, 255, 255, 100%);"
                                       )
        self.tab3_status.setFont(font_status)
        self.tab3_status.setAlignment(Qt.AlignCenter)

        self.tab3_tables_status = LabelBox_status("Empty Table List")
        self.tab3_tables_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                       "color: rgba(255, 255, 255, 100%);"
                                       )
        self.tab3_tables_status.setFont(font_status)
        self.tab3_tables_status.setAlignment(Qt.AlignCenter)

        self.tab3.layout.addWidget(self.tab3_imageLabel, 0, 0, 1, 6)
        self.tab3.layout.addWidget(self.tab3_title, 1, 0, 4, 6)
        self.tab3.layout.addWidget(self.tab3_db_select_label, 6, 0, 1, 1)
        self.tab3.layout.addWidget(self.tab3_db_select, 6, 1, 1, 2)
        self.tab3.layout.addWidget(self.tab3_sensor_select_label, 7, 0, 1, 1)
        self.tab3.layout.addWidget(self.tab3_sensor_select, 7, 1, 1, 2)
        self.tab3.layout.addWidget(self.tab3_sensor_graph_remove_button, 7, 3, 1, 1)
        self.tab3.layout.addWidget(self.tab3_sensor_graph_clear_button, 7, 4, 1, 1)
        self.tab3.layout.addWidget(self.tab3_sensor_graph_add_button, 7, 5, 1, 1)
        self.tab3.layout.addWidget(self.tab3_tables_status, 8, 0, 1, 6)
        self.tab3.layout.addWidget(self.tab3_text_edit_widget, 9, 0, 2, 6)
        self.tab3.layout.addWidget(self.tab3_status, 14, 0, 1, 6)
        self.tab3.layout.addWidget(self.tab3_sensor_graph_button, 15, 0, 1, 2)
        self.tab3.layout.addWidget(self.tab3_sensor_line_graph_button, 15, 2, 1, 2)
        self.tab3.layout.addWidget(self.tab3_sensor_export_button, 15, 4, 1, 2)


        self.tab3.setLayout(self.tab3.layout)





        # Table to be displayed
        self.tab3_table_display = []
        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        self.tab3_db_select.clear()
        self.tab3_db_select.addItems(db_table)
        temp_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab3_db_select.currentText())
        try:
            self.tab3_sensor_select.clear()
            self.tab3_sensor_select.addItems(temp_dbms.return_list_of_graph())
        except TypeError:
            pass

        self.tab3_db_select.currentTextChanged.connect(self.tab3_on_db_changed)
        self.tab3_sensor_graph_button.clicked.connect(self.tab3_sensor_graph_button_action)
        self.tab3_sensor_line_graph_button.clicked.connect(self.tab3_sensor_line_graph_button_action)
        self.tab3_sensor_graph_add_button.clicked.connect(self.tab3_sensor_graph_add_button_action)
        self.tab3_sensor_graph_remove_button.clicked.connect(self.tab3_sensor_graph_remove_button_action)
        self.tab3_sensor_graph_clear_button.clicked.connect(self.tab3_sensor_graph_clear_button_action)
        self.tab3_sensor_export_button.clicked.connect(self.tab3_graph_export_button_action)






        self.tab4_title = LabelBox_title("Error List Graphical Interface")
        self.tab4_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab4_title.setAlignment(Qt.AlignCenter)
        self.tab4_title.setFont(font_title)


        self.tab4_Err_display_all_button = PushBut(self)
        self.tab4_Err_display_all_button.setText("Display All")
        self.tab4_Err_display_all_button.setFont(font_but)

        self.tab4_graph_filter_button = PushBut(self)
        self.tab4_graph_filter_button.setText("Display Filtered")
        self.tab4_graph_filter_button.setFont(font_but)

        self.tab4_graph_export_button = PushBut(self)
        self.tab4_graph_export_button.setText("Export Filtered SN")
        self.tab4_graph_export_button.setFont(font_but)


        self.tab4_blacklist_count_label = LabelBox("Black List Count Per Log")
        self.tab4_blacklist_count_label.setFont(font_label)

        self.tab4_blacklist_low_limit_txt = TextBox(self)
        self.tab4_blacklist_low_limit_txt.setPlaceholderText("Low Limit Count")

        self.tab4_blacklist_high_limit_txt = TextBox(self)
        self.tab4_blacklist_high_limit_txt.setPlaceholderText("High Limit Count")

        self.tab4_blacklist_select_label = LabelBox("Please Select BlackList")
        self.tab4_blacklist_select_label.setFont(font_label)
        self.tab4_blacklist_select = ComboBox()

        self.tab4_model_select_label = LabelBox("Please Select Model")
        self.tab4_model_select_label.setFont(font_label)
        self.tab4_model_select = ComboBox()

        self.tab4_text_edit_widget = QPlainTextEdit()
        self.tab4_text_edit_widget.setReadOnly(True)


        self.tab4.layout.addWidget(self.tab4_imageLabel, 0, 0, 1, 6)
        self.tab4.layout.addWidget(self.tab4_title, 1, 0, 1, 6)
        self.tab4.layout.addWidget(self.tab4_blacklist_select_label, 2, 0, 1, 1)
        self.tab4.layout.addWidget(self.tab4_blacklist_select, 2, 1, 1, 5)
        self.tab4.layout.addWidget(self.tab4_blacklist_count_label, 3, 0, 1, 1)
        self.tab4.layout.addWidget(self.tab4_blacklist_low_limit_txt, 3, 1, 1, 2)
        self.tab4.layout.addWidget(self.tab4_blacklist_high_limit_txt, 3, 3, 1, 3)
        self.tab4.layout.addWidget(self.tab4_model_select_label, 4, 0, 1, 1)
        self.tab4.layout.addWidget(self.tab4_model_select, 4, 1, 1, 5)
        self.tab4.layout.addWidget(self.tab4_text_edit_widget, 5, 0, 2, 6)
        #self.tab4.layout.addWidget(self.tab4_bar_graph, 6, 0, 4, 6)
        self.tab4.layout.addWidget(self.tab4_Err_display_all_button, 13, 0, 1, 2)
        self.tab4.layout.addWidget(self.tab4_graph_filter_button, 13, 2, 1, 2)
        self.tab4.layout.addWidget(self.tab4_graph_export_button, 13, 4, 1, 2)
        self.tab4.setLayout(self.tab4.layout)

        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        self.tab4_model_select.clear()
        self.tab4_model_select.addItems(db_table)

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab4_model_select.currentText())
        self.tab4_blacklist_select.clear()
        self.tab4_blacklist_select.addItems(self.dbms.return_all_blacklist())

        txtInfo = graphFigure.check_err_low_high(self.tab4_blacklist_select.currentText(),
                                                 self.tab4_model_select.currentText(),
                                                 self.tab4_model_select.currentText())
        self.tab4_blacklist_low_limit_txt.setText(str(txtInfo[0]))
        self.tab4_blacklist_high_limit_txt.setText(str(txtInfo[1]))

        self.tab4_Err_display_all_button.clicked.connect(self.tab4_Err_display_all_button_action)
        self.tab4_graph_filter_button.clicked.connect(self.tab4_graph_filter_button_action)
        self.tab4_graph_export_button.clicked.connect(self.tab4_export_button_action)
        self.tab4_blacklist_select.currentTextChanged.connect(self.tab4_on_blacklist_changed)
        self.tab4_model_select.currentTextChanged.connect(self.tab4_on_model_changed)




# Tab 5 start
        self.tab5_title = LabelBox_title("Sensor vs Sensor Graphical Interface")
        self.tab5_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab5_title.setAlignment(Qt.AlignCenter)
        self.tab5_title.setFont(font_title)
        self.tab5_model_select_label = LabelBox("Please Select The Model")
        self.tab5_model_select_label.setFont(font_label)

        self.tab5_table_x_select_label = LabelBox("Please Select The Table (Horizontal)")
        self.tab5_table_x_select_label.setFont(font_label)

        self.tab5_table_y_select_label = LabelBox("Please Select The Table for (Verticle)")
        self.tab5_table_y_select_label.setFont(font_label)

        self.tab5_test_type_select_label = LabelBox("Please Select Test Type")
        self.tab5_test_type_select_label.setFont(font_label)

        self.tab5_graph_select_label = LabelBox("Please Select the Table to Plot")
        self.tab5_graph_select_label.setFont(font_label)

        self.tab5_model_select = ComboBox()
        self.tab5_table_x_select = ComboBox()
        self.tab5_table_y_select = ComboBox()
        self.tab5_test_type_select = ComboBox()
        self.tab5_graph_select = ComboBox()

        self.tab5_text_edit_widget = QPlainTextEdit()
        self.tab5_text_edit_widget.setReadOnly(True)

        self.tab5_status = LabelBox_status("Please Create a Table before Graphing")
        self.tab5_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                       "color: rgba(255, 255, 255, 100%);"
                                       )
        self.tab5_status.setFont(font_status)
        self.tab5_status.setAlignment(Qt.AlignCenter)

        self.tab5_sensor_relationship_graph_button = PushBut(self)
        self.tab5_sensor_relationship_graph_button.setText("Graph Relationship")
        self.tab5_sensor_relationship_graph_button.setFont(font_but)

        self.tab5_sensor_difference_graph_button = PushBut(self)
        self.tab5_sensor_difference_graph_button.setText("Graph Difference")
        self.tab5_sensor_difference_graph_button.setFont(font_but)

        self.tab5_sensor_graph_button = PushBut(self)
        self.tab5_sensor_graph_button.setText("Graph Scatter")
        self.tab5_sensor_graph_button.setFont(font_but)

        self.tab5_sensor_export_button = PushBut(self)
        self.tab5_sensor_export_button.setText("Export")
        self.tab5_sensor_export_button.setFont(font_but)

        self.tab5_sensor_create_button = PushBut(self)
        self.tab5_sensor_create_button.setText("Create Table")
        self.tab5_sensor_create_button.setFont(font_but)



        self.tab5.layout.addWidget(self.tab5_imageLabel, 0, 0, 1, 6)
        self.tab5.layout.addWidget(self.tab5_title, 1, 0, 1, 6)
        self.tab5.layout.addWidget(self.tab5_model_select_label, 5, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_model_select, 5, 2, 1, 4)
        self.tab5.layout.addWidget(self.tab5_table_x_select_label, 6, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_table_x_select, 6, 2, 1, 4)
        self.tab5.layout.addWidget(self.tab5_table_y_select_label, 7, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_table_y_select, 7, 2, 1, 4)
        self.tab5.layout.addWidget(self.tab5_test_type_select_label, 8, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_test_type_select, 8, 2, 1, 4)
        self.tab5.layout.addWidget(self.tab5_text_edit_widget, 9, 0, 2, 6)
        self.tab5.layout.addWidget(self.tab5_status, 14, 0, 1, 6)
        self.tab5.layout.addWidget(self.tab5_graph_select_label, 15, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_graph_select, 15, 2, 1, 4)
        self.tab5.layout.addWidget(self.tab5_sensor_create_button, 16, 0, 1, 2)
        self.tab5.layout.addWidget(self.tab5_sensor_relationship_graph_button, 16, 2, 1, 1)
        self.tab5.layout.addWidget(self.tab5_sensor_difference_graph_button, 16, 3, 1, 1)
        self.tab5.layout.addWidget(self.tab5_sensor_graph_button, 16, 4, 1, 1)
        self.tab5.layout.addWidget(self.tab5_sensor_export_button, 16, 5, 1, 1)


        self.tab5.setLayout(self.tab5.layout)

        try:
            db_table = self.dbms.return_list_of_vs_graph()
        except:
            db_table = []
            print("no data yet")


        if len(db_table)>2:
            db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
        self.tab5_graph_select.clear()
        self.tab5_graph_select.addItems(db_table)

        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        self.tab5_model_select.clear()
        self.tab5_model_select.addItems(db_table)

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab5_model_select.currentText())
        db_table = []
        try:
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
            db_table.sort()
            self.tab5_table_x_select.clear()
            self.tab5_table_x_select.addItems(db_table)
            self.tab5_table_y_select.clear()
            self.tab5_table_y_select.addItems(db_table)
        except:
            print("no data yet tab5_table_x_y")
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab5_test_type_select.clear()
        self.tab5_test_type_select.addItems(test_type_list)

        # customized vs graph
        try:
            db_table = self.dbms.return_list_of_vs_graph()
        except:
            db_table = []
            print("no data yet")

        self.tab5_model_select.currentTextChanged.connect(self.tab5_on_model_changed)
        self.tab5_sensor_create_button.clicked.connect(self.tab5_create_view)
        self.tab5_sensor_export_button.clicked.connect(self.tab5_export_button_action)
        self.tab5_sensor_graph_button.clicked.connect(self.tab5_graph_button_action)
        self.tab5_sensor_relationship_graph_button.clicked.connect(self.tab5_graph_relationship_button_action)
        self.tab5_sensor_difference_graph_button.clicked.connect(self.tab5_graph_difference_button_action)

        # Tab 6 start
        self.tab6_title = LabelBox_title("Sensor vs Sensor Graphical Interface")
        self.tab6_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab6_title.setAlignment(Qt.AlignCenter)
        self.tab6_title.setFont(font_title)
        self.tab6_model_select_label = LabelBox("Please Select The Model")
        self.tab6_model_select_label.setFont(font_label)

        self.tab6_table_x_select_label = LabelBox("Please Select The Table for X")
        self.tab6_table_x_select_label.setFont(font_label)

        self.tab6_table_y_select_label = LabelBox("Please Select The Table for Y")
        self.tab6_table_y_select_label.setFont(font_label)

        self.tab6_test_type_select_label = LabelBox("Please Select Test Type")
        self.tab6_test_type_select_label.setFont(font_label)

        self.tab6_boundary_label = LabelBox("Graph(Limits and Intervals)")
        self.tab6_boundary_label.setFont(font_label)

        self.tab6_x_low_limit_txt = TextBox(self)
        self.tab6_x_low_limit_txt.setPlaceholderText("Low Limit for x")

        self.tab6_x_high_limit_txt = TextBox(self)
        self.tab6_x_high_limit_txt.setPlaceholderText("High Limit for x")

        self.tab6_y_low_limit_txt = TextBox(self)
        self.tab6_y_low_limit_txt.setPlaceholderText("Low Limit for y")

        self.tab6_y_high_limit_txt = TextBox(self)
        self.tab6_y_high_limit_txt.setPlaceholderText("High Limit for y")

        self.tab6_x_interval_txt = TextBox(self)
        self.tab6_x_interval_txt.setPlaceholderText("Interval for X")

        self.tab6_y_interval_txt = TextBox(self)
        self.tab6_y_interval_txt.setPlaceholderText("Interval for y")

        self.tab6_model_select = ComboBox()
        self.tab6_table_x_select = ComboBox()
        self.tab6_table_y_select = ComboBox()
        self.tab6_test_type_select = ComboBox()

        self.tab6_text_edit_widget = QPlainTextEdit()
        self.tab6_text_edit_widget.setReadOnly(True)

        self.tab6_status = LabelBox_status("Please Fill in Above Before Graphing")
        self.tab6_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                       "color: rgba(255, 255, 255, 100%);"
                                       )
        self.tab6_status.setFont(font_status)
        self.tab6_status.setAlignment(Qt.AlignCenter)

        self.tab6_sensor_graph_button = PushBut(self)
        self.tab6_sensor_graph_button.setText("Graph")
        self.tab6_sensor_graph_button.setFont(font_but)

        self.tab6.layout.addWidget(self.tab6_imageLabel, 0, 0, 1, 6)
        self.tab6.layout.addWidget(self.tab6_title, 1, 0, 1, 6)
        self.tab6.layout.addWidget(self.tab6_model_select_label, 5, 0, 1, 2)
        self.tab6.layout.addWidget(self.tab6_model_select, 5, 2, 1, 4)
        self.tab6.layout.addWidget(self.tab6_table_x_select_label, 6, 0, 1, 2)
        self.tab6.layout.addWidget(self.tab6_table_x_select, 6, 2, 1, 4)
        self.tab6.layout.addWidget(self.tab6_table_y_select_label, 7, 0, 1, 2)
        self.tab6.layout.addWidget(self.tab6_table_y_select, 7, 2, 1, 4)
        self.tab6.layout.addWidget(self.tab6_test_type_select_label, 8, 0, 1, 2)
        self.tab6.layout.addWidget(self.tab6_test_type_select, 8, 2, 1, 4)

        self.tab6.layout.addWidget(self.tab6_boundary_label, 9, 0, 2, 1)
        self.tab6.layout.addWidget(self.tab6_x_low_limit_txt, 9, 1, 1, 1)
        self.tab6.layout.addWidget(self.tab6_x_high_limit_txt, 9, 2, 1, 1)
        self.tab6.layout.addWidget(self.tab6_x_interval_txt, 9, 3, 1, 1)
        self.tab6.layout.addWidget(self.tab6_y_low_limit_txt, 10, 1, 1, 1)
        self.tab6.layout.addWidget(self.tab6_y_high_limit_txt, 10, 2, 1, 1)
        self.tab6.layout.addWidget(self.tab6_y_interval_txt, 10, 3, 1, 1)

        self.tab6.layout.addWidget(self.tab6_text_edit_widget, 15, 0, 2, 6)
        self.tab6.layout.addWidget(self.tab6_status, 20, 0, 1, 6)
        self.tab6.layout.addWidget(self.tab6_sensor_graph_button, 22, 0, 1, 4)

        self.tab6.setLayout(self.tab6.layout)

        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        self.tab6_model_select.clear()
        self.tab6_model_select.addItems(db_table)

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab6_model_select.currentText())
        db_table = []
        try:
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
            db_table.sort()
            self.tab6_table_x_select.clear()
            self.tab6_table_x_select.addItems(db_table)
            self.tab6_table_y_select.clear()
            self.tab6_table_y_select.addItems(db_table)
        except:
            print("no data yet tab6_table_x_y")
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab6_test_type_select.clear()
        self.tab6_test_type_select.addItems(test_type_list)

        try:
            self.tab6_x_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_x_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
        except:
            pass
        try:
            self.tab6_y_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_y_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
        except:
            pass

        self.tab6_model_select.currentTextChanged.connect(self.tab6_on_model_changed)
        self.tab6_table_x_select.currentTextChanged.connect(self.tab6_on_x_sensor_table_changed)
        self.tab6_table_y_select.currentTextChanged.connect(self.tab6_on_y_sensor_table_changed)
        self.tab6_test_type_select.currentTextChanged.connect(self.tab6_on_test_type_changed)
        self.tab6_sensor_graph_button.clicked.connect(self.tab6_graph_button_action)

    # Check all on-click logic
    @pyqtSlot(int)
    def onStateChange(self, state):
        if self.sender() == self.tab2_max_checkBox:
            if state == Qt.Checked:
                self.tab2_avg_checkBox.setChecked(False)
        elif self.sender() == self.tab2_avg_checkBox:
            if state == Qt.Checked:
                self.tab2_max_checkBox.setChecked(False)

    def restore_db_action(self):


        if self.tab1_cur_sqlpath.text() == 'Empty':
            print("Please Select a sql File")
            self.status.setText("Please Select a sql File")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            self.status.setText("SQL is Being Restored, Please Wait")
            self.status.setStyleSheet("QLabel {background-color : blue; color : white;}")
            self.status.repaint()

            subprocess.call("cd C:\\Program Files\\PostgreSQL\\11\\bin &&set \"PGPASSWORD=fortinet\"&&pg_restore -C -d postgres -v -h localhost -p 5432 -U postgres "+self.tab1_cur_sqlpath.text(), shell=True)

            self.text_edit_widget.appendPlainText("The sql file ("+self.tab1_cur_sqlpath.text()+") has been successfully added to the data base")

            db_table = []
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
            self.tab2_model_select.clear()
            self.tab2_model_select.addItems(db_table)
            self.tab3_db_select.clear()
            self.tab3_db_select.addItems(db_table)
            self.tab4_model_select.clear()
            self.tab4_model_select.addItems(db_table)
            self.tab5_model_select.clear()
            self.tab5_model_select.addItems(db_table)
            self.tab6_model_select.clear()
            self.tab6_model_select.addItems(db_table)


            self.status.setText("SQL Restored Successfully")
            self.status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                      "color: rgba(0, 0, 0, 100%);")

    def select_sql_action(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Please Select A SQL File", "",
                                                  "SQL Files (*.sql)", options=options)
        if fileName:
            self.tab1_cur_sqlpath.setText(fileName)

    def tab6_graph_button_action(self):
        self.fig1 = plt.figure(FigureClass=graphFigure)
        self.fig1.plot_h_bar(model = self.tab6_model_select.currentText(), testtype = self.tab6_test_type_select.currentText(),
                             table1 = self.tab6_table_x_select.currentText(), table2 = self.tab6_table_y_select.currentText(),
                             minx = float(self.tab6_x_low_limit_txt.text()), maxx = float(self.tab6_x_high_limit_txt.text()),
                             intervalx = float(self.tab6_x_interval_txt.text()), miny = float(self.tab6_y_low_limit_txt.text()),
                             maxy = float(self.tab6_y_high_limit_txt.text()), intervaly = float(self.tab6_y_interval_txt.text()))

    def tab6_on_x_sensor_table_changed(self):
        try:
            self.tab6_x_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_x_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
        except:
            pass

    def tab6_on_y_sensor_table_changed(self):
        try:
            self.tab6_y_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_y_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
        except:
            pass

    def tab6_on_test_type_changed(self):
        try:
            self.tab6_x_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_x_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_x_select.currentText(),
                                                self.tab6_model_select.currentText(),self.tab6_test_type_select.currentText()))
            self.tab6_y_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),
                                                self.tab6_test_type_select.currentText()))
            self.tab6_y_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab6_table_y_select.currentText(),
                                                self.tab6_model_select.currentText(),
                                                self.tab6_test_type_select.currentText()))
        except:
            pass

    def tab6_on_model_changed(self):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab6_model_select.currentText())
        db_table = []
        try:
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
            db_table.sort()
            self.tab6_table_x_select.clear()
            self.tab6_table_x_select.addItems(db_table)
            self.tab6_table_y_select.clear()
            self.tab6_table_y_select.addItems(db_table)
        except:
            print("no data yet tab6_table_x_y")
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab6_test_type_select.clear()
        self.tab6_test_type_select.addItems(test_type_list)


    def tab3_on_db_changed(self):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab3_db_select.currentText())
        try:
            db_table = self.dbms.return_list_of_graph()
        except:
            db_table = []
            print("no data yet")

        self.tab3_sensor_select.clear()
        self.tab3_sensor_select.addItems(db_table)

    def tab5_on_model_changed(self):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab5_model_select.currentText())
        db_table = []
        try:
            db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
            db_table.sort()
            self.tab5_table_x_select.clear()
            self.tab5_table_x_select.addItems(db_table)
            self.tab5_table_y_select.clear()
            self.tab5_table_y_select.addItems(db_table)
        except:
            print("no data yet tab5_table_x_y")
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab5_test_type_select.clear()
        self.tab5_test_type_select.addItems(test_type_list)

        # customized vs graph
        try:
            db_table = self.dbms.return_list_of_vs_graph()
        except:
            db_table = []
            print("no data yet")

        if len(db_table)>2:
            db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
        self.tab5_graph_select.clear()
        self.tab5_graph_select.addItems(db_table)







    def save_parsing_info(self):

        if len(self.tab1_model_text.text()) != 6:
            self.status.setText("Please Check the Model (First 6 letters of the Serial Number)")
            self.text_edit_widget.appendPlainText("Please Check the Model (First 6 letters of the Serial Number)")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not self.tab1_table_1_text.text():
            self.status.setText("Please Enter a Name for the Table")
            self.text_edit_widget.appendPlainText("Please Enter a Name for the Table")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not self.tab1_reg_text.text():
            self.status.setText("Regex cannot be empty")
            self.text_edit_widget.appendPlainText("Regex cannot be empty")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            try:
                re.compile(self.tab1_reg_text.text())
                if not self.tab1_base_text.text():
                    buttonReply = QMessageBox.question(self, 'Warning message',
                                                       "No base command entered, so there will be no reference line, Do you want to Continue?",
                                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if buttonReply == QMessageBox.Yes:
                        pass
                    else:
                        return
                try:

                    if os.path.exists('database_create_info.csv'):
                        with open('database_create_info.csv', 'a') as out:
                            field_names = ['TableName', 'BaseCommand', 'Regex', 'ReferenceBuffer', 'Unit', 'Result']
                            csv_out = csv.DictWriter(out, fieldnames=field_names, lineterminator="\n")
                            test = dict(zip(field_names, [self.tab1_table_1_text.text(), self.tab1_base_text.text(),
                                                          self.tab1_reg_text.text(), self.tab1_ReferenceBuffer.text(), self.tab1_Unit.text(), self.tab1_log_condition_dropdown.currentText()]))
                            csv_out.writerow(test)
                    else:
                        with open('database_create_info.csv', 'a') as out:
                            field_names = ['TableName', 'BaseCommand', 'Regex', 'ReferenceBuffer', 'Unit', 'Result']
                            csv_out = csv.DictWriter(out, fieldnames=field_names, lineterminator="\n")
                            csv_out.writeheader()
                            test = dict(zip(field_names, [self.tab1_table_1_text.text(), self.tab1_base_text.text(),
                                                          self.tab1_reg_text.text(),
                                                          self.tab1_ReferenceBuffer.text(),
                                                          self.tab1_Unit.text(),self.tab1_log_condition_dropdown.currentText()]))
                            csv_out.writerow(test)
                    self.text_edit_widget.appendPlainText("Conditions above has been successfully add to the csv file")
                    self.status.setText("Conditions above has been successfully add to the csv file")
                    self.status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                              "color: rgba(0, 0, 0, 100%);")
                except PermissionError:
                    self.status.setText("Please Close database_create_info.csv")
                    self.text_edit_widget.appendPlainText("database_create_info.csv is opened, cannot access")
                    self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
            except re.error:
                self.status.setText("Invalid Regex")
                self.text_edit_widget.appendPlainText("Invalid Regex")
                self.status.setStyleSheet("QLabel {background-color : red; color : white;}")




    def tab4_on_blacklist_changed(self):

        txtInfo = graphFigure.check_err_low_high(self.tab4_blacklist_select.currentText(),
                                                 self.tab4_model_select.currentText(),self.tab4_model_select.currentText())
        self.tab4_blacklist_low_limit_txt.setText(str(txtInfo[0]))
        self.tab4_blacklist_high_limit_txt.setText(str(txtInfo[1]))

    def tab4_on_model_changed(self):

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab4_model_select.currentText())
        self.tab4_blacklist_select.clear()
        self.tab4_blacklist_select.addItems(self.dbms.return_all_blacklist())

    def tab5_create_max_view(self, sensor_x, sensor_y, baseview):
        view_name = "Horizontal_Based_AVG"

        query_val = {'sx': sensor_x, 'sy': sensor_y, 'vn': view_name}

        base_query = "CREATE VIEW \"{vn}\" AS SELECT DISTINCT(serial_number), test_date, test_type, \"{sx}_reading\", \"{sy}_reading\" " \
                     "FROM \""+baseview+"\" WHERE (serial_number, \"{sx}_reading\", \"{sy}_reading\") " \
                     "IN (SELECT serial_number, \"{sx}_reading\", \"{sy}_reading\" " \
                     "FROM ( SELECT serial_number, \"{sx}_reading\", \"{sy}_reading\", " \
                     "row_number() over (partition by serial_number " \
                     "ORDER BY \"{sx}_reading\" DESC, \"{sy}_reading\" DESC) " \
                     "AS rn " \
                     "FROM \""+baseview+"\") AS X WHERE rn = 1) " \
                     "ORDER BY serial_number"

        query = base_query.format(**query_val)

        #print(query)

        try:
            test = ["".join(x) for x in
                    self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
            self.tab5_status.setText("Custom Table {} Already Exists, the data will be overwritten".format(view_name))
            self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            self.dbms.execute_query("DROP VIEW \"{}\";".format(view_name))
            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText(
                    "Custom Table:\" {} \" Created Successfully, but the data will be overwritten".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, sensor_x, sensor_y)
                # update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")

                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()
                self.tab5_graph_select.addItems(db_table)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        except TypeError:

            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText("Custom Table:\" {} \" Created Successfully".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, sensor_x, sensor_y)
                # update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")

                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()
                self.tab5_graph_select.addItems(db_table)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        view_name = "Vertical_Based_AVG"

        query_val = {'sx': sensor_x, 'sy': sensor_y, 'vn': view_name}

        base_query = "CREATE VIEW \"{vn}\" AS SELECT DISTINCT(serial_number), test_date, test_type, \"{sx}_reading\", \"{sy}_reading\" " \
                     "FROM \""+baseview+"\" WHERE (serial_number, \"{sx}_reading\", \"{sy}_reading\") " \
                     "IN (SELECT serial_number, \"{sx}_reading\", \"{sy}_reading\" " \
                     "FROM ( SELECT serial_number, \"{sx}_reading\", \"{sy}_reading\", " \
                     "row_number() over (partition by serial_number " \
                     "ORDER BY \"{sy}_reading\" DESC,\"{sx}_reading\" DESC) " \
                     "AS rn " \
                     "FROM \""+baseview+"\") AS X WHERE rn = 1) " \
                     "ORDER BY serial_number"

        query = base_query.format(**query_val)

        #print(query)

        try:
            test = ["".join(x) for x in
                    self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
            self.tab5_status.setText("Custom Table {} Already Exists, the data will be overwritten".format(view_name))
            self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            self.dbms.execute_query("DROP VIEW \"{}\";".format(view_name))
            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText(
                    "Custom Table:\" {} \" Created Successfully, but the data will be overwritten".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, sensor_x, sensor_y)
                # update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")

                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()                
                self.tab5_graph_select.addItems(db_table)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        except TypeError:

            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText("Custom Table:\" {} \" Created Successfully".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, sensor_x, sensor_y)
                # update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")
                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()
                self.tab5_graph_select.addItems(db_table)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")

    def tab5_create_view(self):

        self.dbms.create_main_vs_graph_table()
        table_x = self.tab5_table_x_select.currentText()
        table_y = self.tab5_table_y_select.currentText()
        model = self.tab5_model_select.currentText()
        testType = self.tab5_test_type_select.currentText()
        view_name = table_x + "_VS_" + table_y + "_" + testType

        query_val = {'tx': table_x, 'ty': table_y,
                     'tt': self.tab5_test_type_select.currentText(), 'vn': view_name,
                     'model': self.tab5_model_select.currentText()}

        sql_dict = {
            'type_check': "AND \"{tx}\".test_type = '{tt}'"
        }

        base_query = "CREATE VIEW \"{vn}\" AS SELECT \"{tx}\".serial_number," \
                     "\"{tx}\".test_date, " \
                     "\"{tx}\".test_type, " \
                     "AVG(\"{tx}\".reading) AS \"{tx}_reading\"," \
                     "AVG(\"{ty}\".reading) AS \"{ty}_reading\"" \
                     " FROM \"{tx}\" " \
                     "INNER JOIN\"{ty}\" " \
                     "ON \"{tx}\".serial_number = \"{ty}\".serial_number " \
                     "AND \"{tx}\".ref_line_number = \"{ty}\".ref_line_number " \
                     "AND \"{tx}\".test_date = \"{ty}\".test_date " \
                     "WHERE \"{tx}\".reading IS NOT NULL " \
                     "AND \"{ty}\".reading IS NOT NULL " \
                     "AND \"{tx}\".serial_number LIKE '{model}%%'"

        if query_val['tt'] != "All":
            base_query = base_query + sql_dict['type_check']

        base_query = base_query + "GROUP BY(\"{tx}\".serial_number, \"{tx}\".test_date, \"{tx}\".test_type)"

        query = base_query.format(**query_val) + "ORDER BY \"{}\".serial_number".format(table_x)
        #print(query)
        try:
            test = ["".join(x) for x in
                    self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
            self.tab5_status.setText("Custom Table {} Already Exists, the data will be overwritten".format(view_name))
            self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            self.dbms.execute_query("DROP VIEW \"{}\" CASCADE;".format(view_name))
            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText(
                    "Custom Table:\" {} \" Created Successfully, but the data will be overwritten".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, table_x, table_y)

                # update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")

                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()
                self.tab5_graph_select.addItems(db_table)
                self.tab5_create_max_view(table_x, table_y, view_name)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        except TypeError:

            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab5_status.setText("Custom Table:\" {} \" Created Successfully".format(view_name))
                self.tab5_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.dbms.main_sensor_vs_graph_insert(view_name, table_x,table_y)
                #update dropdown
                try:
                    db_table = self.dbms.return_list_of_vs_graph()
                except:
                    db_table = []
                    print("no data yet")


                if len(db_table)>2:
                    db_table = db_table[len(db_table) - 3::-1] + db_table[len(db_table) - 2:]
                self.tab5_graph_select.clear()
                self.tab5_graph_select.addItems(db_table)
                self.tab5_create_max_view(table_x,table_y,view_name)

            except TypeError:
                self.tab5_status.setText("Issue Creating The Custom Table")
                self.tab5_status.setStyleSheet("QLabel {background-color : red; color : white;}")




    def tab5_graph_button_action(self):

        graph_sensor = self.dbms.return_column_names(self.tab5_graph_select.currentText())
        if graph_sensor:
            self.fig1 = plt.figure(FigureClass=graphFigure)
            self.fig1.plot_scatter(self.tab5_graph_select.currentText(), graph_sensor[3], graph_sensor[4], self.tab5_model_select.currentText())
        else:
            self.tab5_text_edit_widget.appendPlainText(
                "Please Select a Table to Graph")

    def tab5_export_button_action(self):
        try:
            self.dbms.vs_graph_to_csv(self.tab5_graph_select.currentText())
            self.tab5_text_edit_widget.appendPlainText(
                "Export Successfully")
        except:
            self.tab5_text_edit_widget.appendPlainText("Failed to Export")

    def tab5_graph_relationship_button_action(self):

        graph_sensor = self.dbms.return_column_names(self.tab5_graph_select.currentText())

        if graph_sensor:
            self.fig1 = plt.figure(FigureClass=graphFigure)
            self.fig1.plot_single_table_line_graph(self.tab5_graph_select.currentText(), graph_sensor[3],
                                                   graph_sensor[4], self.tab5_model_select.currentText())
        else:
            self.tab5_text_edit_widget.appendPlainText(
                "Please Select a Table to Graph")

    def tab5_graph_difference_button_action(self):

        graph_sensor = self.dbms.return_column_names(self.tab5_graph_select.currentText())
        if graph_sensor:
            self.fig1 = plt.figure(FigureClass=graphFigure)
            self.fig1.plot_single_table_line_difference_graph(self.tab5_graph_select.currentText(), graph_sensor[3],
                                                   graph_sensor[4], self.tab5_model_select.currentText())
        else:
            self.tab5_text_edit_widget.appendPlainText(
                "Please Select a Table to Graph")


    def tab2_on_model_changed(self):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.tab2_model_select.currentText())

        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_sensor("sensor_to_unit")]
        db_table.sort()
        self.tab2_table_1_select.clear()
        self.tab2_table_1_select.addItems(db_table)
        test_type_list = self.dbms.return_test_type()
        test_type_list.append("All")
        self.tab2_test_type_select.clear()
        self.tab2_test_type_select.addItems(test_type_list)


    def tab2_on_sensor_table_changed(self):
        try:
            self.tab2_graph_low_limit_txt.setText(
                self.dbms.return_sensor_min_max('min', self.tab2_table_1_select.currentText(),self.tab2_model_select.currentText(),self.tab2_test_type_select.currentText()))
            self.tab2_graph_high_limit_txt.setText(
                self.dbms.return_sensor_min_max('max', self.tab2_table_1_select.currentText(),self.tab2_model_select.currentText(),self.tab2_test_type_select.currentText()))
        except:
            pass

    def tab4_export_button_action(self):
        try:
            self.dbms.to_csv_err_filter(self.tab4_blacklist_select.currentText(), self.tab4_model_select.currentText(), int(self.tab4_blacklist_low_limit_txt.text()), int(self.tab4_blacklist_high_limit_txt.text()))
            self.tab4_text_edit_widget.appendPlainText(
                "Export Successfully")
        except:
            self.tab4_text_edit_widget.appendPlainText("Failed to Export")

    def tab3_graph_export_button_action(self):
        if len(self.tab3_table_display) == 0:
            self.tab3_text_edit_widget.appendPlainText("Add at Least One Table to Export")
            self.tab3_status.setText("Please Add at Least One Table to Export")
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        else:
            try:
                backend_database.MyDatabase.to_csv(self.tab3_table_display)
                self.tab3_text_edit_widget.appendPlainText("Export Successfully, zip Files includes:\" {} \" and its Summary ".format(",".join(self.tab3_table_display)))
                self.tab3_status.setText("Export Successfully, zip Files includes:\" {} \"  and its Summary".format(",".join(self.tab3_table_display)))
                self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
            except:
                self.tab3_text_edit_widget.appendPlainText("Failed to Export")
                self.tab3_status.setText("Failed to Export")
                self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")

    def tab4_graph_filter_button_action(self):

        try:
            lower_limit = int(self.tab4_blacklist_low_limit_txt.text())
            higher_limit = int(self.tab4_blacklist_high_limit_txt.text())


            graph_data = graphFigure.check_graph_empty(self.tab4_blacklist_select.currentText(),lower_limit,higher_limit,self.tab4_model_select.currentText())

            if graph_data[0] and graph_data[1] and graph_data[2]:
                self.fig1 = plt.figure(FigureClass=graphFigure)

                self.tab4_text_edit_widget.appendPlainText("Blacklist keyword Appears in "+str(round(graph_data[2],2))+"% of Total Logs")
                self.fig1.plotbar_err_condition(self.tab4_blacklist_select.currentText(),lower_limit, higher_limit, self.tab4_model_select.currentText(),graph_data[0],graph_data[1],self.tab4_model_select.currentText())

            else:
                self.tab4_text_edit_widget.appendPlainText("The Selected Range Has No data")
        except ValueError:
            print("Please enter integer for the limits")
            self.tab4_text_edit_widget.appendPlainText("Please ONLY Enter Integer For The Limits")


    def tab4_Err_display_all_button_action(self):
        self.fig1 = plt.figure(FigureClass=graphFigure)
        try:
            self.fig1.plotbar_err_all(self.tab4_model_select.currentText())
        except IndexError:
            self.tab4_text_edit_widget.appendPlainText(
                self.tab4_model_select.currentText()+" has no display data")

    def tab3_sensor_graph_remove_button_action(self):
        try:
            self.tab3_table_display.remove(self.tab3_sensor_select.currentText())

            self.tab3_text_edit_widget.appendPlainText("Table:\" {} \" Removed Successfully".format(self.tab3_sensor_select.currentText()))


            self.tab3_status.setText("New Table List Includes:\n\" {} \" ".format(",   ".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                           "color: rgba(0, 0, 0, 100%);"
                                           )
            self.tab3_tables_status.setText("New Table List Includes:\n\" {} \" ".format(",   ".join(self.tab3_table_display)))
            self.tab3_tables_status.setStyleSheet("background-color: rgba(133, 88, 91, 100%);"
                                                  "color: rgba(255, 255, 255, 100%);"
                                                  )
        except ValueError:
            self.tab3_text_edit_widget.appendPlainText("Table {} is Not in The List".format(self.tab3_sensor_select.currentText()))
            self.tab3_status.setText("Failed to delete {} Table remains as :\" {} \" ".format(self.tab3_sensor_select.currentText(),",".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")

    def tab3_sensor_graph_clear_button_action(self):
            self.tab3_table_display = []

            self.tab3_text_edit_widget.appendPlainText("Clear Table Successfully".format(self.tab3_sensor_select.currentText()))


            self.tab3_status.setText("The Table List is Empty, please Add Table")
            self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                           "color: rgba(0, 0, 0, 100%);"
                                           )
            self.tab3_tables_status.setText("Empty Table List")
            self.tab3_tables_status.setStyleSheet("background-color: rgba(50, 50, 50, 100%);"
                                                  "color: rgba(255, 255, 255, 100%);"
                                                  )

    def tab3_sensor_graph_add_button_action(self):
        if self.tab3_sensor_select.currentText() in self.tab3_table_display:
            self.tab3_text_edit_widget.appendPlainText(
                "Table {} is Already in The List".format(self.tab3_sensor_select.currentText()))
            self.tab3_status.setText(
                "Failed to add {} \nTable remains as :\" {} \" ".format(self.tab3_sensor_select.currentText(),
                                                                         ",".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            self.tab3_text_edit_widget.appendPlainText(
                "Table {} is Added to the List".format(self.tab3_sensor_select.currentText()))
            self.tab3_table_display.append(self.tab3_sensor_select.currentText())
            self.tab3_status.setText("New Table List Includes:\n\" {} \" ".format(",    ".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                           "color: rgba(0, 0, 0, 100%);"
                                           )
            self.tab3_tables_status.setText("New Table List Includes:\n\" {} \" ".format(",   ".join(self.tab3_table_display)))
            self.tab3_tables_status.setStyleSheet("background-color: rgba(133, 88, 91, 100%);"
                                                  "color: rgba(255, 255, 255, 100%);"
                                                  )

    def tab3_sensor_graph_button_action(self):

        if len(self.tab3_table_display) == 0:
            self.tab3_text_edit_widget.appendPlainText("Please Select Table to Graph")
            self.tab3_status.setText("Please Select Table to Graph New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif len(self.tab3_table_display) > 3:
            self.tab3_text_edit_widget.appendPlainText("Cannot Graph more than 3 Tables \n New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
            self.tab3_status.setText("Cannot Graph more than 3 Tables")
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not self.unit_compare(self.tab3_table_display):
            self.tab3_text_edit_widget.appendPlainText("Cannot display table with different \n unit New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
            self.tab3_status.setText("Cannot display table with different unit")
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not backend_database.MyDatabase.graph_interval_compare(self.tab3_table_display):
            self.tab3_text_edit_widget.appendPlainText(
                "Cannot display table with different \n interval New Table List Includes:\n\" {} \" ".format(
                    ",".join(self.tab3_table_display)))
            self.tab3_status.setText("Cannot display table with different interval")
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            try:
                self.tab3_text_edit_widget.appendPlainText("Please Check the Pop Up Window \n New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
                self.tab3_status.setText("Please Check the Pop Up Window")
                self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.fig1 = plt.figure(FigureClass=graphFigure)

                filter_graph = list(set(self.tab3_table_display))
                self.fig1.plotbar_sensor(filter_graph)

            except ValueError as e:
                print(e)
                self.fig1 = ""
                self.tab3_text_edit_widget.appendPlainText("Cannot display table with different interval")
                self.tab3_status.setText("Cannot display table with different interval")
                self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            except RuntimeError as e:
                print(e)
                self.tab3_text_edit_widget.appendPlainText("Issue Displaying Bar Graph Table, Please Try Again")
                self.tab3_status.setText("Issue Displaying Table, Please Try Again")
                self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")

    def tab3_sensor_line_graph_button_action(self):

        if len(self.tab3_table_display) == 0:
            self.tab3_text_edit_widget.appendPlainText("Please Select Table to Graph")
            self.tab3_status.setText("Please Select Table to Graph New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not self.unit_compare(self.tab3_table_display):
            self.tab3_text_edit_widget.appendPlainText("Cannot display table with different \n unit New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
            self.tab3_status.setText("Cannot display table with different unit")
            self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            try:
                self.tab3_text_edit_widget.appendPlainText("Please Check the Pop Up Window \n New Table List Includes:\n\" {} \" ".format(",".join(self.tab3_table_display)))
                self.tab3_status.setText("Please Check the Pop Up Window")
                self.tab3_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
                self.fig1 = plt.figure(FigureClass=graphFigure)

                filter_graph = list(set(self.tab3_table_display))
                self.fig1.plot_line_graph(filter_graph)

            except ValueError as e:
                print(e)
                self.fig1 = ""
                self.tab3_text_edit_widget.appendPlainText("Error Graphing, Please Check your Data")
                self.tab3_status.setText("Error Graphing, Please Chekc your Data")
                self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            except RuntimeError as e:
                print(e)
                self.tab3_text_edit_widget.appendPlainText("Issue Displaying Line Graph Table, Please Try Again")
                self.tab3_status.setText("Issue Displaying Table, Please Try Again")
                self.tab3_status.setStyleSheet("QLabel {background-color : red; color : white;}")


    def unit_compare(self, table_list):
        model_list = [x[:6] for x in table_list]


        table_c = len(table_list)
        if table_c == 1:
            return True

        for idx, table in enumerate(table_list):
            temp_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[idx])

            if idx == 0:
                previous_unit = temp_dbms.return_unit_from_graph(table_list[idx])
            else:
                if previous_unit != temp_dbms.return_unit_from_graph(table_list[idx]):
                    return False
                previous_unit = temp_dbms.return_unit_from_graph(table_list[idx])
        return True


        # def unit_compare(self, table_list):
        #     model_list = [x[:6] for x in table_list]
        #
        #     table_c = len(table_list)
        #     if table_c == 1:
        #         return True
        #     elif table_c == 2:
        #         table1_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[0])
        #         table1_unit = table1_dbms.return_unit_from_graph(table_list[0])
        #         table2_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[1])
        #         table2_unit = table2_dbms.return_unit_from_graph(table_list[1])
        #         if table1_unit == table2_unit:
        #             return True
        #         return False
        #     elif table_c == 3:
        #         table1_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[0])
        #         table1_unit = table1_dbms.return_unit_from_graph(table_list[0])
        #         table2_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[1])
        #         table2_unit = table2_dbms.return_unit_from_graph(table_list[1])
        #         table3_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[2])
        #         table3_unit = table3_dbms.return_unit_from_graph(table_list[2])
        #         if table1_unit == table2_unit and table1_unit == table3_unit:
        #             return True
        #         return False


    def time_range(self):

        s = [x.rjust(2, '0') for x in self.tab2_from_select.text().split("/")]
        range_low = s[2] + "-" + s[0] + "-" + s[1] + " " + "00:00:00"

        s = [x.rjust(2, '0') for x in self.tab2_to_select.text().split("/")]
        range_high = s[2] + "-" + s[0] + "-" + s[1] + " " + "23:59:59"

        return [range_low,range_high]

    def tab1_time_range(self):

        s = [x.rjust(2, '0') for x in self.tab1_from_select.text().split("/")]
        range_low = s[2] + "-" + s[0] + "-" + s[1] + " " + "00:00:00"

        s = [x.rjust(2, '0') for x in self.tab1_to_select.text().split("/")]
        range_high = s[2] + "-" + s[0] + "-" + s[1] + " " + "23:59:59"

        return [range_low,range_high]

    def tab2_preview_view(self):

        table1 = self.tab2_table_1_select.currentText()
        query_val = {'t1':table1, 'low':self.time_range()[0],
                      'high':self.time_range()[1], 'sn_low':self.tab2_sn_low.text(),
                      'sn_high' : self.tab2_sn_high.text(), 'tt':self.tab2_test_type_select.currentText(), 'model':self.tab2_model_select.currentText()}

        sql_dict = {'date_check': "AND \"{t1}\".test_date >= '{low}' AND \"{t1}\".test_date <= '{high}'",
                    'sn_check': "AND \"{t1}\".serial_number >= '{sn_low}' AND \"{t1}\".serial_number <= '{sn_high}'",
                    'type_check': "AND \"{t1}\".test_type = '{tt}'",'model_check':"AND \"{t1}\".serial_number LIKE '{model}%%'"
                    }

        base_query = "SELECT \"{t1}\".serial_number AS \"Serial Number\"," \
                "\"{t1}\".test_date, " \
                "\"{t1}\".test_type, " \
                "\"{t1}\".line_number AS \"{t1}_Line_Number\"," \
                "\"{t1}\".alarm AS \"{t1}_Alarm\"," \
                "\"{t1}\".reading AS \"{t1}_Reading\"" \
                "FROM \"{t1}\" " \
                "WHERE \"{t1}\".reading IS NOT NULL "



        if self.tab2_max_checkBox.checkState():
            unique_base_query_top = "SELECT DISTINCT(\"Table1\".serial_number)," \
                                    "\"{t1}\".test_type, " \
                                    "\"{t1}\".alarm ," \
                                    "\"Table1\".reading " \
                                    "FROM (SELECT \"{t1}\".serial_number, MAX(\"{t1}\".reading) AS reading " \
                                    "FROM \"{t1}\" GROUP BY serial_number) AS \"Table1\" " \
                                    "INNER JOIN \"{t1}\" " \
                                    "ON \"Table1\".serial_number = \"{t1}\".serial_number " \
                                    "WHERE \"{t1}\".reading IS NOT NULL "
        elif self.tab2_avg_checkBox.checkState():
            unique_base_query_top = "SELECT DISTINCT(\"Table1\".serial_number)," \
                                    "\"{t1}\".test_type, " \
                                    "\"{t1}\".alarm ," \
                                    "\"Table1\".reading " \
                                    "FROM (SELECT \"{t1}\".serial_number, AVG(\"{t1}\".reading) AS reading " \
                                    "FROM \"{t1}\" GROUP BY serial_number) AS \"Table1\" " \
                                    "INNER JOIN \"{t1}\" " \
                                    "ON \"Table1\".serial_number = \"{t1}\".serial_number " \
                                    "WHERE \"{t1}\".reading IS NOT NULL "


        if self.tab2_max_checkBox.checkState() or self.tab2_avg_checkBox.checkState():
            if query_val['low'] and query_val['high']:
                unique_base_query_top = unique_base_query_top + sql_dict['date_check']
            if query_val['sn_low'] and query_val['sn_high']:
                unique_base_query_top = unique_base_query_top + sql_dict['sn_check']
            if query_val['tt'] != "All":
                unique_base_query_top = unique_base_query_top + sql_dict['type_check']
            unique_base_query_top = unique_base_query_top + sql_dict['model_check']

            if self.tab2_max_checkBox.checkState() or self.tab2_avg_checkBox.checkState():
                query = unique_base_query_top.format(**query_val) + " ORDER BY reading, \"Table1\".serial_number"


        else:
            if query_val['low'] and query_val['high']:
                base_query = base_query + sql_dict['date_check']
            if query_val['sn_low'] and query_val['sn_high']:
                base_query = base_query + sql_dict['sn_check']
            if query_val['tt'] != "All":
                base_query = base_query + sql_dict['type_check']
            base_query = base_query + sql_dict['model_check']

            query = base_query.format(**query_val)+ "ORDER BY reading"

        if self.tab2_max_checkBox.checkState() or self.tab2_avg_checkBox.checkState():
            t_c = ['Serial Number', 'Test Type', table1 + ' Alarm',
                   table1 + ' Reading']
        else:
            t_c = ['Serial Number', 'Test Date', 'Test Type', table1 + ' LineNumber', table1 + ' Alarm',
                   table1 + ' Reading']

        t_l = len(t_c)
        # create the view
        self.tab2_tableWidget.setColumnCount(t_l)
        self.tab2_tableWidget.setHorizontalHeaderLabels(t_c)
        self.tab2_tableWidget.setRowCount(0)  # reset table
        rows = 3000
        self.tab2_tableWidget.setRowCount(rows)
        previous_length = 0

        try:
            for row in self.dbms.query_return_all_data(query):
                for c in range(t_l):
                    self.tab2_tableWidget.setItem(previous_length, c, QTableWidgetItem(str(row[c])))
                previous_length += 1

            self.tab2_status.setText("Please Check The Table Below:")
            self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                           "color: rgba(0, 0, 0, 100%);")
        except TypeError:
            print("empty table")

    def isfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def tab2_create_view(self):

        table1 = self.tab2_table_1_select.currentText()
        model = self.tab2_model_select.currentText()
        testtype = self.tab2_test_type_select.currentText()


        view_name = self.tab2_save_view_txt.text().upper()
        view_name = view_name.replace('_graph','')
        if not view_name:
            view_name =  model+"_"+table1+"_"+testtype+"_Customized"

        if view_name[:6] != model:
            view_name = model + "_" + view_name

        query_val = {'t1':table1, 'low':self.time_range()[0],
                      'high':self.time_range()[1], 'sn_low':self.tab2_sn_low.text(),
                      'sn_high' : self.tab2_sn_high.text(), 'tt':self.tab2_test_type_select.currentText(), 'vn':view_name, 'model':self.tab2_model_select.currentText()}

        sql_dict = {'date_check': "AND \"{t1}\".test_date >= '{low}' AND \"{t1}\".test_date <= '{high}'",
                    'sn_check': "AND \"{t1}\".serial_number >= '{sn_low}' AND \"{t1}\".serial_number <= '{sn_high}'",
                    'type_check': "AND \"{t1}\".test_type = '{tt}'",'model_check':"AND \"{t1}\".serial_number LIKE '{model}%%'"
                    }

        base_query = "CREATE VIEW \"{vn}\" AS SELECT \"{t1}\".serial_number," \
                "\"{t1}\".test_date, " \
                "\"{t1}\".test_type, " \
                "\"{t1}\".line_number ," \
                "\"{t1}\".alarm ," \
                "\"{t1}\".reading " \
                "FROM \"{t1}\" " \
                "WHERE \"{t1}\".reading IS NOT NULL "

        if self.tab2_max_checkBox.checkState():
            unique_base_query_top = "CREATE VIEW \"{vn}\" AS SELECT DISTINCT(\"Table1\".serial_number)," \
                                    "\"{t1}\".test_type, " \
                                    "\"{t1}\".test_date, " \
                                    "\"{t1}\".alarm ," \
                                    "\"Table1\".reading " \
                                    "FROM (SELECT \"{t1}\".serial_number, MAX(\"{t1}\".reading) AS reading " \
                                    "FROM \"{t1}\" GROUP BY serial_number) AS \"Table1\" " \
                                    "INNER JOIN \"{t1}\" " \
                                    "ON \"Table1\".serial_number = \"{t1}\".serial_number " \
                                    "WHERE \"{t1}\".reading IS NOT NULL "

        elif self.tab2_avg_checkBox.checkState():
            unique_base_query_top = "CREATE VIEW \"{vn}\" AS SELECT DISTINCT(\"Table1\".serial_number)," \
                                    "\"{t1}\".test_type, " \
                                    "\"{t1}\".test_date, " \
                                    "\"{t1}\".alarm ," \
                                    "\"Table1\".reading " \
                                    "FROM (SELECT \"{t1}\".serial_number, AVG(\"{t1}\".reading) AS reading " \
                                    "FROM \"{t1}\" GROUP BY serial_number) AS \"Table1\" " \
                                    "INNER JOIN \"{t1}\" " \
                                    "ON \"Table1\".serial_number = \"{t1}\".serial_number " \
                                    "WHERE \"{t1}\".reading IS NOT NULL "

        if self.tab2_max_checkBox.checkState() or self.tab2_avg_checkBox.checkState():
            if query_val['low'] and query_val['high']:
                unique_base_query_top = unique_base_query_top + sql_dict['date_check']
            if query_val['sn_low'] and query_val['sn_high']:
                unique_base_query_top = unique_base_query_top + sql_dict['sn_check']
            if query_val['tt'] != "All":
                unique_base_query_top = unique_base_query_top + sql_dict['type_check']
            unique_base_query_top = unique_base_query_top + sql_dict['model_check']

            query = unique_base_query_top.format(**query_val) +" ORDER BY reading, \"Table1\".serial_number"

        else:
            if query_val['low'] and query_val['high']:
                base_query = base_query + sql_dict['date_check']
            if query_val['sn_low'] and query_val['sn_high']:
                base_query = base_query + sql_dict['sn_check']
            if query_val['tt'] != "All":
                base_query = base_query + sql_dict['type_check']
            base_query = base_query + sql_dict['model_check']

            query = base_query.format(**query_val) + "ORDER BY reading"

        print(query)
        try:
            test = ["".join(x) for x in self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
            self.tab2_status.setText("Custom Table {} Already Exists, the data will be overwritten".format(view_name))
            self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")
            self.dbms.execute_query("DROP VIEW \"{}\";".format(view_name))
            self.dbms.execute_query(query)
            try:
                test = ["".join(x) for x in
                        self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                self.tab2_status.setText("Custom Table:\" {} \" Created Successfully, but the data will be overwritten".format(view_name))
                self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                               "color: rgba(0, 0, 0, 100%);"
                                               )
            except TypeError:
                self.tab2_status.setText("Issue Creating The Custom Table")
                self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")

        except TypeError:

                self.dbms.execute_query(query)
                try:
                    test = ["".join(x) for x in self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(view_name))]
                    self.tab2_status.setText("Custom Table:\" {} \" Created Successfully".format(view_name))
                    self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                                   "color: rgba(0, 0, 0, 100%);"
                                                   )
                except TypeError:
                    self.tab2_status.setText("Issue Creating The Custom Table")
                    self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")


        if self.isfloat(self.tab2_graph_low_limit_txt.text()) and self.isfloat(self.tab2_graph_high_limit_txt.text()) and self.isfloat(self.tab2_graph_interval_txt.text()):

            # Create table for graph
            self.graph_table_name = view_name+"_graph"
            self.dbms.create_main_graph_table()
            try:
                test = ["".join(x) for x in self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(self.graph_table_name))]
                self.tab2_status.setText("Custom Table {} Already Exists, the data will be overwritten".format(self.graph_table_name))
                self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")
                self.dbms.execute_query("DROP TABLE \"{}\";".format(self.graph_table_name))
                #CREATE AND INSERT TABLE
                self.dbms.create_graph_table(view_name)  # _graph is added during table creation
                self.dbms.main_sensor_graph_update(self.graph_table_name,
                                                   float(self.tab2_graph_low_limit_txt.text()),
                                                   float(self.tab2_graph_high_limit_txt.text()),
                                                   float(self.tab2_graph_interval_txt.text()))


                self.table_min = self.dbms.return_graph_column_info('start_graph', self.graph_table_name)
                self.table_max = self.dbms.return_graph_column_info('end_graph', self.graph_table_name)
                self.graph_interval = self.dbms.return_graph_column_info('interval', self.graph_table_name)
                self.unit = self.dbms.return_unit(self.tab2_table_1_select.currentText())

                # Insert the graphing table (when duplicate)
                for val in np.arange(self.table_min, self.table_max, self.graph_interval):
                    count = self.dbms.return_sensor_count(view_name, round(val, 2),round(val + self.graph_interval,2))
                    self.dbms.sensor_interval_insert(self.graph_table_name, str(round(val, 2)) + "-" + str(
                        round(val + self.graph_interval, 2)), count, self.unit)
                    #to eliminate 0 count
                    # if count == 0:
                    #     pass
                    # else:
                    #     self.dbms.sensor_interval_insert(self.graph_table_name, str(round(val, 2)) + "-" + str(
                    #         round(val + self.graph_interval, 2)), count, self.unit)

                # update the list
                self.tab2_custom_view_select.clear()
                self.tab2_custom_view_select.addItems(self.dbms.return_list_of_views())

                self.tab3_sensor_select.clear()
                try:
                    self.tab3_sensor_select.addItems(self.dbms.return_list_of_graph())
                except TypeError:
                    print("NOOO DATA YET")
                db_table = []
                db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
                self.tab3_db_select.setCurrentIndex(db_table.index(self.tab2_model_select.currentText()))
                self.tab3_sensor_select.clear()
                try:
                    self.tab3_sensor_select.addItems(self.dbms.return_list_of_graph())
                except TypeError:
                    print("NOOO DATA YET")


                try:
                    test = ["".join(x) for x in
                            self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(self.graph_table_name))]
                    self.tab2_status.setText("Custom Table:\" {} \" Created Successfully, but the data will be overwritten".format(self.graph_table_name))
                    self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                                   "color: rgba(0, 0, 0, 100%);"
                                                   )
                except TypeError:
                    self.tab2_status.setText("Issue Creating The Custom Table")
                    self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")

            except TypeError:

                    #CREATE AND INSERT TABLE
                    self.dbms.create_graph_table(view_name)  # _graph is added during table creation
                    self.dbms.main_sensor_graph_insert(self.graph_table_name,
                                                       float(self.tab2_graph_low_limit_txt.text()),
                                                       float(self.tab2_graph_high_limit_txt.text()),
                                                       float(self.tab2_graph_interval_txt.text()))

                    self.table_min = self.dbms.return_graph_column_info('start_graph', self.graph_table_name)
                    self.table_max = self.dbms.return_graph_column_info('end_graph', self.graph_table_name)
                    self.graph_interval = self.dbms.return_graph_column_info('interval', self.graph_table_name)
                    self.unit = self.dbms.return_unit(self.tab2_table_1_select.currentText())

                    # Insert the graphing table
                    for val in np.arange(self.table_min, self.table_max, self.graph_interval):
                        count = self.dbms.return_sensor_count(view_name, round(val, 2),round(val + self.graph_interval, 2))
                        self.dbms.sensor_interval_insert(self.graph_table_name, str(round(val, 2)) + "-" + str(
                            round(val + self.graph_interval, 2)), count, self.unit)
                        # if count == 0:
                        #     pass
                        # else:
                        #     self.dbms.sensor_interval_insert(self.graph_table_name, str(round(val, 2)) + "-" + str(
                        #         round(val + self.graph_interval, 2)), count, self.unit)



                    # update the list
                    self.tab2_custom_view_select.clear()
                    self.tab2_custom_view_select.addItems(self.dbms.return_list_of_views())

                    self.tab3_sensor_select.clear()
                    try:
                        self.tab3_sensor_select.addItems(self.dbms.return_list_of_graph())
                    except TypeError:
                        print("NOOO DATA YET")
                    db_table = []
                    db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
                    self.tab3_db_select.setCurrentIndex(db_table.index(self.tab2_model_select.currentText()))
                    self.tab3_sensor_select.clear()
                    try:
                        self.tab3_sensor_select.addItems(self.dbms.return_list_of_graph())
                    except TypeError:
                        print("NOOO DATA YET")

                    try:
                        test = ["".join(x) for x in self.dbms.query_return_all_data("SELECT to_regclass('\"{}\"')".format(self.graph_table_name))]
                        self.tab2_status.setText("Custom Table:\" {} \" Created Successfully".format(view_name))
                        self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                                       "color: rgba(0, 0, 0, 100%);"
                                                       )
                    except TypeError:
                        self.tab2_status.setText("Issue Creating The Custom Table")
                        self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            print("Missing Graph parameters")
            self.tab2_status.setText("Missing Graph parameters")
            self.tab2_status.setStyleSheet("QLabel {background-color : red; color : white;}")







#Create Table
    def tab2_show_view(self):
        try:
            t_c = self.dbms.return_column_names(self.tab2_custom_view_select.currentText())
            t_l = len(t_c)
            # create the view
            self.tab2_tableWidget.setColumnCount(t_l)
            self.tab2_tableWidget.setHorizontalHeaderLabels(t_c)
            self.tab2_tableWidget.setRowCount(0)  # reset table
            rows = 3000
            self.tab2_tableWidget.setRowCount(rows)
            previous_length = 0
            for row in self.dbms.return_all_data(self.tab2_custom_view_select.currentText()):
                for c in range(t_l):
                    self.tab2_tableWidget.setItem(previous_length, c, QTableWidgetItem(str(row[c])))
                previous_length += 1

            self.tab2_status.setText(
                "Please Check The Table Below: \n -----{}-----".format(self.tab2_custom_view_select.currentText()))
            self.tab2_status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                           "color: rgba(0, 0, 0, 100%);"
                                           )
            # self.tab2_tableWidget.move(0, 0)
        except TypeError:
            print("No table selected")
            self.tab2_status.setText("No table selected")
            self.tab2_status.setStyleSheet("background-color: red;"
                                           "color: white;"
                                           )



    def start_button(self):


        #verify cvs file
        csvlist = []
        try:
            with open('database_create_info.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    csvlist.append(row['TableName'])
        except:
            self.status.setText("Please Create CSV File first")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")


        global logfile, start_time
        logfile = self.filepath_box.text()
        model = self.tab1_model_text.text().upper()
        testtype = list(self.tab1_test_type_text.text().split(","))

        if len(csvlist) != len(set(csvlist)):
            self.status.setText("Sensor table cannot have the same name")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not logfile:
            print("Please Enter the file path")
            self.status.setText("Please Enter the file path")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif len(self.tab1_model_text.text()) != 6:
            print("Please Enter the first 6 letters of the SN")
            self.status.setText("Please Enter the first 6 letters of the SN")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        elif not self.tab1_test_type_text.text():
            print("Please Enter at least one test type separate by commas (ITS, HTS,SFC)")
            self.status.setText("Please Enter at least one test type seperate by commas (ITS, HTS,SFC)")
            self.status.setStyleSheet("QLabel {background-color : red; color : white;}")
        else:
            try:
                self.app_thread.sig1.disconnect()
                self.tab1_sig.disconnect()
            except:
                pass

            start_time = datetime.datetime.now()
            # Establish the connection between Main signal (tab1_sig) to slot (start_source)
            try:
                self.tab1_sig.connect(self.app_thread.start_source)
            except TypeError as e:
                print(e)
            except AttributeError as e:
                print(e)
            except ValueError as e:
                print(e)
            except IOError as e:
                print(e)
            # Change the status label box
            self.status.setText("The Test Is Running, Please Wait.")
            self.status.setStyleSheet("background-color: rgba(153, 204, 255, 90%);"
                                      "color: rgba(0, 0, 0, 100%);"
                                      )

            self.tab1_sig.emit({"model":model, "testtype":testtype, "from_time":self.tab1_time_range()[0], "to_time":self.tab1_time_range()[1], "manuel":self.tab1_checkBox.checkState()})

            # Establish the connection from thread signal back to main (to know when the thread is finished running)
            # end_info will be executed when the thread is finished

            self.app_thread.sig1.connect(self.end_info)

            # Start the thread
            self.app_thread.start()
            self.startbutton.setEnabled(False)
            self.startbutton.setText("Running!!!")
            self.app_thread.running = False


    # Task perform after finishing running the thread.
    def end_info(self, info):
        global start_time
        model = self.tab1_model_text.text().upper()
        print("in end_info")
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model)


        # COMBOBOX Content


        # COMBOBOX Content
        db_table = []
        db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        self.tab2_model_select.clear()
        self.tab2_model_select.addItems(db_table)
        self.tab3_db_select.clear()
        self.tab3_db_select.addItems(db_table)
        self.tab4_model_select.clear()
        self.tab4_model_select.addItems(db_table)
        self.tab5_model_select.clear()
        self.tab5_model_select.addItems(db_table)
        self.tab6_model_select.clear()
        self.tab6_model_select.addItems(db_table)


        self.tab2_model_select.setCurrentIndex(db_table.index(model))
        self.tab3_db_select.setCurrentIndex(db_table.index(model))
        self.tab4_model_select.setCurrentIndex(db_table.index(model))
        self.tab5_model_select.setCurrentIndex(db_table.index(model))
        self.tab6_model_select.setCurrentIndex(db_table.index(model))

        #
        # self.tab4_blacklist_select.clear()
        # self.tab4_blacklist_select.addItems(self.dbms.return_all_blacklist())
        # self.tab4_model_select.clear()
        # self.model = [''.join(item) for item in self.dbms.return_all_model()]
        # self.model.append('All')
        # self.tab4_model_select.addItems(self.model)
        #
        # test_type_list = self.dbms.return_test_type()
        # test_type_list.append("All")
        # self.tab5_test_type_select.clear()
        # self.tab5_test_type_select.addItems(test_type_list)
        # try:
        #     db_table = []
        #     db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        #     self.tab5_model_select.clear()
        #     self.tab5_model_select.addItems(db_table)
        # except TypeError:
        #     print('No Data Yet (tab 5 model)')
        #
        # #customized vs graph
        # try:
        #     db_table = self.dbms.return_list_of_vs_graph()
        # except:
        #     db_table = []
        #     print("no data yet")
        #
        # db_table = []
        # db_table = db_table + [''.join(item) for item in self.dbms.return_all_model()]
        # self.tab6_model_select.clear()
        # self.tab6_model_select.addItems(db_table)

        print("Test Finished! {} ".format(info))

        # for sensor in info["sensor_data"]:
        #     self.text_edit_widget.appendPlainText("{} Table Created Successfully".format(sensor))
        #
        # for keyword in info["blacklist_data"]:
        #     self.text_edit_widget.appendPlainText("{} Table Created Successfully".format(keyword))


        duration = datetime.datetime.now() - start_time
        duration = duration.seconds

        print("---Create Table Duration {} Seconds---".format(duration))
        self.text_edit_widget.appendPlainText("-----Create Table Duration {} Seconds-----".format(duration))



        # Set the status label box

        self.status.setText("Process Ended Successfully")
        self.status.setStyleSheet("background-color: rgba(102, 255, 51, 90%);"
                                  "color: rgba(0, 0, 0, 100%);"
                                  )
        QMessageBox.about(self, "Process Status", "The Process is Finish, Please Check the Table")
        # Re-enabling the start button
        self.startbutton.setEnabled(True)
        self.startbutton.setText("Create DataBase ⯈")






# Thread Class
class Qapp_thread(QtCore.QThread):

    # string signal
    sig1 = pyqtSignal(dict)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.table_data = ""
        self.running = False



    # Function call when first connect to the thread
    def start_source(self, info):
        # pass the content in "Info" to "start_source" slot, where info has the full command form the main app
        self.table_data = info
        print("The Test Will Start Soon!")

    def run(self):
        self.running = True


        print("Test Starting!")


        engine = create_engine("postgresql://postgres:fortinet@localhost/"+self.table_data['model'])
        if database_exists(engine.url):
            pass
            # Delete PostgreSQL database
            #drop_database(engine.url)
            # Create empty PostgreSQL database
            #create_database(engine.url)
        # Otherwise
        else:
            # Create empty PostgreSQL database
            create_database(engine.url)

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=self.table_data['model'])
        # self.dbms.create_model_sensor_info_table()
        self.dbms.create_sensor_unit_table()
        self.dbms.create_main_blacklist_table()


        data_scraper = DataBaseInfo(self.table_data['model'])
        if self.table_data['manuel']:
            print("Parsing Manuel")
            try:
                data_scraper.manual_log_parser(logfile,self.table_data['model'],self.table_data['testtype'])
            except:
                print("Please check your Manuel file path")
        else:
            print("Parsing CM")
            try:
                data_scraper.tgz_unzip(logfile,self.table_data['model'],self.table_data['testtype'],self.table_data['from_time'],self.table_data['to_time'])
                data_scraper.folder_parser(logfile, self.table_data['model'], self.table_data['testtype'],
                                           self.table_data['from_time'], self.table_data['to_time'])
            except:
                print("Please check your CM file path")
        #
        #self.sig1.emit(table_data)
        self.sig1.emit({'Test':'Finish'})



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    desktop = QtWidgets.QApplication.desktop()
    resolution = desktop.availableGeometry()
    myapp = App()
    # myapp.setWindowOpacity(0.95)
    myapp.show()
    myapp.move(resolution.center() - myapp.rect().center())
    sys.exit(app.exec_())
