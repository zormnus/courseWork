# Form implementation generated from reading ui file '.\Tasks_Widget.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(596, 344)
        Form.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(90, 67, 134, 255), stop:1 rgba(255, 255, 255, 255));")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(240, 10, 101, 20))
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.updateBtn = QtWidgets.QPushButton(Form)
        self.updateBtn.setGeometry(QtCore.QRect(200, 290, 111, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.updateBtn.sizePolicy().hasHeightForWidth())
        self.updateBtn.setSizePolicy(sizePolicy)
        self.updateBtn.setStyleSheet("QPushButton {\n"
"    background-color: #8993c8;\n"
"    border: 2px solid #aa55ff;\n"
"    border-radius:10px;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    border: 1px solid #333333;\n"
"    background-color: #aa55ff;\n"
"}")
        self.updateBtn.setText("")
        self.updateBtn.setObjectName("updateBtn")
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(10, 50, 571, 231))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(50)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(50)
        self.tableWidget.verticalHeader().setMinimumSectionSize(50)
        self.tableWidget.verticalHeader().setStretchLastSection(True)
        self.addTaskBtn = QtWidgets.QPushButton(Form)
        self.addTaskBtn.setGeometry(QtCore.QRect(350, 290, 61, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addTaskBtn.sizePolicy().hasHeightForWidth())
        self.addTaskBtn.setSizePolicy(sizePolicy)
        self.addTaskBtn.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.addTaskBtn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\../sources/add_icon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.addTaskBtn.setIcon(icon)
        self.addTaskBtn.setIconSize(QtCore.QSize(24, 24))
        self.addTaskBtn.setObjectName("addTaskBtn")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Ваши задачи"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
