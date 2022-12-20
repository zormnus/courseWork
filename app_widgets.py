import logging

import user_info

from PyQt6.QtCore import Qt, QDate
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QMessageBox,
    QLineEdit, QVBoxLayout, QTableWidget,
    QTableWidgetItem
)

import config
from Widgets import Auth_Widget, Reg_Widget, Main_Widget, Tasks_Widget
from db_worker import Database_Functional
import Lines_Parsing



class AuthorizationWindow(QMainWindow):
    def __init__(self):
        super(AuthorizationWindow, self).__init__()
        self.ui = Auth_Widget.Ui_MainWindow()
        self.start_ui()

        self.reg_widget = None
        self.main_widget = None

    def start_ui(self):
        self.ui.setupUi(self)
        self.ui.label_2.setPixmap(QPixmap('./sources/auth-icon.png'))
        self.setWindowIcon(QIcon('sources/car-icon.png'))
        self.ui.loginEnter.setPlaceholderText('Введите логин')
        self.ui.passwordEnter.setPlaceholderText('Введите пароль')
        self.ui.regBtn.clicked.connect(self.reg_open)
        self.ui.authBtn.clicked.connect(self.authorize)

    def authorize(self):
        login, password = self.ui.loginEnter.text(), self.ui.passwordEnter.text()
        error_msg = QMessageBox()
        error_msg.setWindowTitle('Ошибка авторизации')
        error_msg.setIcon(QMessageBox.Icon.Warning)

        if login == '' or password == '':
            error_msg.setText('Заполните все поля!')
            error_msg.exec()
            return

        if Database_Functional.get_instance(config.user_name).user_authorization(login, password):
            user_info.User.login = login
            pos_id = Database_Functional.get_instance(config.user_name).get_UserPos_by_login(login)
            user_info.User.id = Database_Functional.get_instance(config.user_name).get_UserId_by_login(login)
            user_info.User.position = user_info.Positions.ADMIN if pos_id == 1 \
                else user_info.Positions.MECHANIC if pos_id == 2 \
                else user_info.Positions.ACCOUNTANT

            logging.info("Успешная авторизация")
            self.main_widget = MainWindow()
            self.hide()
            self.main_widget.show()

        else:
            error_msg.setText('Введены неверный логин/пароль')
            error_msg.exec()
            return

    def reg_open(self):
        self.reg_widget = RegistrationWindow()
        self.hide()
        self.reg_widget.show()


class RegistrationWindow(QWidget):
    def __init__(self):
        super(RegistrationWindow, self).__init__()
        self.ui = Reg_Widget.Ui_Form()
        self.start_ui()

        self.auth_widget = None

    def start_ui(self):
        self.ui.setupUi(self)
        self.ui.email_error.setVisible(False)
        self.ui.phone_number_error.setVisible(False)
        self.setWindowIcon(QIcon('./sources/car-icon.png'))
        self.ui.icon.setPixmap(QPixmap('./sources/auth-icon.png'))
        self.ui.passwordIsVisible.setIcon(QIcon('./sources/show_pass_icon32.png'))
        self.ui.passwordIsVisible.stateChanged.connect(lambda: self.set_passwordStatus())

        if user_info.User.position == user_info.Positions.UNDEFINED:
            self.ui.first_name.setPlaceholderText('Введите ваше имя')
            self.ui.last_name.setPlaceholderText('Введите вашу фамилию')
            self.ui.email.setPlaceholderText('Введите вашу почту')
            self.ui.login.setPlaceholderText('Введите логин')
            self.ui.password.setPlaceholderText('Введите пароль')
            self.ui.phone_number.setPlaceholderText('Введите номер телефона')

            possible_positions = ['СТО администратор']
            self.ui.positions.addItems(possible_positions)
        else:
            self.ui.first_name.setPlaceholderText('Введите имя сотркудника')
            self.ui.last_name.setPlaceholderText('Введите фамилию сотрудника')
            self.ui.email.setPlaceholderText('Введите почту сотрудника')
            self.ui.login.setPlaceholderText('Введите логин сотрудника')
            self.ui.password.setPlaceholderText('Введите пароль сотрудника')
            self.ui.phone_number.setPlaceholderText('Введите номер телефона сотрудника')

            possible_positions = ['Механик', 'Бухгалтер']
            self.ui.positions.addItems(possible_positions)

        self.ui.regBtn.clicked.connect(self.register)

    def set_passwordStatus(self):
        if self.ui.passwordIsVisible.isChecked():
            self.ui.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.ui.password.setEchoMode(QLineEdit.EchoMode.Password)

    def register(self):
        self.ui.email_error.setVisible(False)
        self.ui.phone_number_error.setVisible(False)
        values = dict([('first_name', self.ui.first_name.text()),
                       ('last_name', self.ui.last_name.text()),
                       ('email', self.ui.email.text()),
                       ('login', self.ui.login.text()),
                       ('password', self.ui.password.text()),
                       ('phone_number', self.ui.phone_number.text()),
                       ('position', self.ui.positions.currentText())])

        match values['position']:
            case 'СТО администратор':
                values['position'] = 1
            case 'Автомеханик':
                values['position'] = 2
            case 'Бухгалтер':
                values['position'] = 3

        msg = QMessageBox()
        for line in values.values():
            if line == '':
                msg.setWindowTitle('Ошибка')
                msg.setText('Вы должны заполнить все поля')
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.exec()
                return

        if not self.check_format():
            return

        if Database_Functional.get_instance(config.user_name).user_registration(user_data=values):
            msg.setWindowTitle('Успех')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText('Вы успешно зарегистрировались')
            msg.exec()
            logging.info("Успешная регистрация!")
            Database_Functional.get_instance(config.user_name).create_user(user_name=values['login'],
                                                                     position=values['position'])

        else:
            msg.setWindowTitle('Ошибка')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Ошибка регистрации')
            msg.exec()
            logging.warning('Ошибка регистрации!')

    def check_format(self) -> bool:
        if not (Lines_Parsing.check_email(self.ui.email.text())) and \
                not (Lines_Parsing.check_phone_number(self.ui.phone_number.text())):
            self.ui.email_error.setVisible(True)
            self.ui.email_error.setText('Неверный формат почты')
            self.ui.phone_number_error.setVisible(True)
            self.ui.phone_number_error.setText('Неверный формат номера')
            return False
        elif not (Lines_Parsing.check_email(self.ui.email.text())):
            self.ui.email_error.setVisible(True)
            self.ui.email_error.setText('Неверный формат почты')
            return False
        elif not (Lines_Parsing.check_phone_number(self.ui.phone_number.text())):
            self.ui.phone_number_error.setVisible(True)
            self.ui.phone_number_error.setText('Неверный формат номера')
            return False
        return True

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.auth_widget = AuthorizationWindow()
        self.hide()
        self.auth_widget.show()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Main_Widget.Ui_Form()
        self.ui.setupUi(self)
        self.start_ui()

        if user_info.User.position == user_info.Positions.MECHANIC\
                or user_info.User.position == user_info.Positions.ADMIN:
            self.ui.tabWidget.addTab(TasksWindow(), 'Ваши задания')

        if user_info.User.position == user_info.Positions.ADMIN:
            self.ui.tabWidget.addTab(RegistrationWindow(), "Добавить сотрудника")

        self.AuthWindow = None

    def start_ui(self):
        self.setLayout(QVBoxLayout())
        self.setWindowIcon(QIcon('./sources/car-icon.png'))
        self.ui.leave_btn.setIcon(QIcon('./sources/leave-icon12.png'))
        self.ui.hello_msg.setText(f"Добро пожаловать, {user_info.User.login}")

        position = 'Администратор СТО' if user_info.User.position == user_info.Positions.ADMIN else \
            'Механик' if user_info.User.position == user_info.User.position.MECHANIC else 'Бухгалтер'
        self.ui.pos_msg.setText(f"Ваша должность: {position}")
        self.ui.leave_btn.clicked.connect(self.leaveToAuth)

    def leaveToAuth(self):
        self.hide()
        self.AuthWindow = AuthorizationWindow()
        self.AuthWindow.show()


class TasksWindow(QWidget):
    def __init__(self):
        super(TasksWindow, self).__init__()
        self.ui = Tasks_Widget.Ui_Form()
        self.ui.setupUi(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        data = Database_Functional.get_instance(config.user_name).get_data(3, with_prepare=True)

        self.tasks_ids = []

        self.ui.tableWidget = QTableWidget(len(data), len(data[0]))
        self.ui.updateBtn.clicked.connect(self.update_clicked)
        self.layout.addWidget(self.ui.tableWidget)
        self.layout.addWidget(self.ui.updateBtn)
        self.ui.tableWidget.setHorizontalHeaderLabels(['Содержание', 'Номер Контракта',
                                                       'Дата создания',
                                                       'Дата выполнения', 'Дедлайн', 'Статус',
                                                       'Автор',
                                                       'ID Исполнителя'])

        self.convert_values(data)
        self.setupTable(data)

    def setupTable(self, data):
        for row in range(len(data)):
            for col in range(len(data[row])):
                if isinstance(data[row][col], QDate):
                    data[row][col] = data[row][col].toString('MMMM d, yyyy')
                if col == 5:
                    if data[row][col] != 'Выполнено':
                        item = QTableWidgetItem(f"{data[row][col]}")
                        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.ui.tableWidget.setItem(row, col, item)
                    else:
                        item = QTableWidgetItem(f"{data[row][col]}")
                        self.ui.tableWidget.setItem(row, col, item)
                else:
                    item = QTableWidgetItem(f"{data[row][col]}")
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    self.ui.tableWidget.setItem(row, col, item)
        self.ui.tableWidget.itemClicked.connect(self.update_task)
        self.ui.tableWidget.resizeColumnsToContents()

    def update_clicked(self):
        new_data = Database_Functional.get_instance(user_info.User.login).get_data(3, with_prepare=True)
        self.ui.tableWidget.clear()
        self.convert_values(new_data)
        self.setupTable(new_data)
        logging.info("task table view was updated!")

    def update_task(self, item):
        if not (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
            return

        if item.checkState() == Qt.CheckState.Checked:
            Database_Functional.get_instance(user_info.User.login).update_task_status(self.tasks_ids[item.row()])

    def convert_values(self, data: list):
        for i in range(len(data)):
            self.tasks_ids.append(data[i][0])
            data[i][0] = Database_Functional.get_instance(config.user_name).get_task_text(int(data[i][0]))
            data[i][5] = "Выполнено" if data[i][5] else "Не выполнено"
            data[i][6] = Database_Functional.get_instance(config.user_name).get_authorName(int(data[i][6]))
