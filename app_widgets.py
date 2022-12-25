import hashlib
import logging

import user_info

from PyQt6.QtCore import Qt, QDate
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QMessageBox,
    QLineEdit, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)

from config import Config
from Widgets import (
    Auth_Widget, Reg_Widget, Main_Widget,
    Tasks_Widget, Contract_Widget, Client_Widget,
    Car_Widget, Tasks_Actions, Completed_Tasks_Widget
)
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

        if Database_Functional.get_instance("postgres").check_user(login, password):
            Config.user_name = login
            Config.db_password = password
            user_info.User.login = login
            pos_id = Database_Functional.get_instance(Config.user_name).get_UserPos_by_login(login)
            user_info.User.id = Database_Functional.get_instance(Config.user_name).get_UserId_by_login(login)
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
        self.ui.car_services.addItems(Database_Functional.get_instance("postgres").get_all_car_services())

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
            self.ui.first_name.setPlaceholderText('Введите имя сотрудника')
            self.ui.last_name.setPlaceholderText('Введите фамилию сотрудника')
            self.ui.email.setPlaceholderText('Введите почту сотрудника')
            self.ui.login.setPlaceholderText('Введите логин сотрудника')
            self.ui.password.setPlaceholderText('Введите пароль сотрудника')
            self.ui.phone_number.setPlaceholderText('Введите номер телефона сотрудника')

            possible_positions = ['Автомеханик', 'Бухгалтер']
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
                       ('position', self.ui.positions.currentText()),
                       ('car_service_name', self.ui.car_services.currentText())])

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

        self.check_format()

        if self.ui.email_error.isVisible() or self.ui.phone_number_error.isVisible():
            return

        if Database_Functional.get_instance("postgres").user_registration(user_data=values):
            msg.setWindowTitle('Успех')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText('Вы успешно зарегистрировались')
            msg.exec()
            logging.info("Успешная регистрация!")

        else:
            msg.setWindowTitle('Ошибка')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Ошибка регистрации')
            msg.exec()
            logging.warning('Ошибка регистрации!')

    def check_format(self):
        if not (Lines_Parsing.check_email(self.ui.email.text())):
            self.ui.email_error.setText("Неверный формат почты")
            self.ui.email_error.setVisible(True)
        if not (Lines_Parsing.check_phone_number(self.ui.phone_number.text())):
            self.ui.phone_number_error.setText("Неверный формат номера телефона")
            self.ui.phone_number_error.setVisible(True)

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

        if user_info.User.position == user_info.Positions.MECHANIC \
                or user_info.User.position == user_info.Positions.ADMIN:
            self.ui.tabWidget.addTab(TasksWindow(), "Ваши задания")

        if user_info.User.position == user_info.Positions.ADMIN:
            self.ui.tabWidget.addTab(RegistrationWindow(), "Добавить сотрудника")

        if user_info.User.position == user_info.Positions.ACCOUNTANT:
            self.ui.tabWidget.addTab(ClientWindow(), "Добавить клиента")
            self.ui.tabWidget.addTab(CarWindow(), "Добавить автомобиль")
            self.ui.tabWidget.addTab(ContractWindow(), "Создать контракт")

        if user_info.User.position == user_info.Positions.ADMIN:
            self.ui.tabWidget.addTab(DisplayReport(), "Отчётность сервиса")

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

        self.layout = QHBoxLayout()

        self.addTaskWindow = None

        self.init_ui()

    def init_ui(self):
        self.setLayout(self.layout)

        self.ui.addTaskBtn.setIcon(QIcon('./sources/add_icon.png'))
        self.ui.addTaskBtn.clicked.connect(self.create_task)

        data = Database_Functional.get_instance(user_info.User.login).get_data(user_info.User.id)

        if data:
            self.ui.tableWidget = QTableWidget(len(data), len(data[0]))
            self.convert_values(data)
            self.setupTable(data)
        else:
            self.ui.tableWidget = QTableWidget()

        self.ui.tableWidget.setHorizontalHeaderLabels(['Содержание', 'Номер Контракта',
                                                       'Дата создания',
                                                       'Дата выполнения', 'Дедлайн', 'Статус',
                                                       'Автор',
                                                       'ID Исполнителя'])
        self.ui.tableWidget.resizeColumnsToContents()

        self.ui.updateBtn.setIcon(QIcon('./sources/update_icon.png'))
        self.ui.updateBtn.clicked.connect(self.update_clicked)
        self.layout.addWidget(self.ui.tableWidget)
        self.layout.addWidget(self.ui.updateBtn)
        self.layout.addWidget(self.ui.addTaskBtn)

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
        new_data = Database_Functional.get_instance(user_info.User.login).get_data(user_info.User.id)
        if new_data:
            self.ui.tableWidget.clearContents()
            self.convert_values(new_data)
            self.setupTable(new_data)
            logging.info("task table view was updated!")

    def create_task(self):
        self.addTaskWindow = CreateTaskWindow()
        self.addTaskWindow.show()

    def update_task(self, item):
        if not (item.flags() & Qt.ItemFlag.ItemIsUserCheckable):
            return

        cur_contract_id = int(self.ui.tableWidget.item(item.row(), 1).text())
        if item.checkState() == Qt.CheckState.Checked:
            Database_Functional.get_instance(user_info.User.login).update_task_status(cur_contract_id)

    @staticmethod
    def convert_values(data: list):
        for i in range(len(data)):
            data[i][0] = Database_Functional.get_instance(Config.user_name).get_task_text(int(data[i][0]))
            data[i][5] = "Выполнено" if data[i][5] else "Не выполнено"
            data[i][6] = Database_Functional.get_instance(Config.user_name).get_authorLogin(int(data[i][6]))


class ContractWindow(QWidget):
    def __init__(self):
        super(ContractWindow, self).__init__()
        self.ui = Contract_Widget.Ui_Form()
        self.ui.setupUi(self)

        self.ui.label_6.setPixmap(QPixmap('./sources/contract_icon64.png'))

        self.init_ui()

    def init_ui(self):
        self.init_comboboxes()

        self.ui.updateBtn.setIcon(QIcon('./sources/update_icon.png'))
        self.ui.updateBtn.clicked.connect(self.on_update)

        self.ui.pushButton.clicked.connect(self.on_createContract)
        pass

    def init_comboboxes(self):
        self.ui.client.addItems(Database_Functional.get_instance(user_info.User.login).get_all_clients())
        self.ui.service.addItems(Database_Functional.get_instance(user_info.User.login).get_all_car_services())
        self.ui.service_type.addItems(Database_Functional.get_instance(user_info.User.login).get_all_services())
        self.ui.techPassport.addItems(
            Database_Functional.get_instance(user_info.User.login).get_all_technical_passports())
        self.ui.autopart.addItems(Database_Functional.get_instance(user_info.User.login).get_all_autoparts())

    def on_update(self):
        self.ui.client.clear()
        self.ui.service.clear()
        self.ui.service_type.clear()
        self.ui.techPassport.clear()
        self.ui.autopart.clear()
        self.init_comboboxes()

    def on_createContract(self):
        values = dict([
            ('cs_name', self.ui.service.currentText()),
            ('cl_email', self.ui.client.currentText()),
            ('passport', self.ui.techPassport.currentText()),
            ('service', self.ui.service_type.currentText()),
            ('part', self.ui.autopart.currentText())
        ])
        msg = QMessageBox()
        if Database_Functional.get_instance(user_info.User.login).create_contract(values):
            msg.setWindowTitle("Успех")
            msg.setText("Контракт был создан")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
        else:
            msg.setWindowTitle("Ошибка")
            msg.setText("Контракт не был создан")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()


class ClientWindow(QWidget):
    def __init__(self):
        super(ClientWindow, self).__init__()
        self.ui = Client_Widget.Ui_Form()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        self.ui.label.setVisible(True)
        self.ui.label.setPixmap(QPixmap('./sources/client_icon64.png'))
        self.ui.phone_number_error.setVisible(False)
        self.ui.email_error.setVisible(False)

        self.ui.updateBtn.setIcon(QIcon('./sources/update_icon.png'))
        self.ui.updateBtn.clicked.connect(self.onUpdate)

        self.ui.name.setPlaceholderText('Введите имя клиента')
        self.ui.surname.setPlaceholderText('Введите фамилию клиента')
        self.ui.email.setPlaceholderText('Введите почту клиента')
        self.ui.phone_number.setPlaceholderText('Введите номер телефона клиента')
        self.ui.createBtn.clicked.connect(self.onCreate)

    def onUpdate(self):
        self.ui.name.clear()
        self.ui.surname.clear()
        self.ui.email.clear()
        self.ui.phone_number.clear()

    def onCreate(self):
        self.ui.email_error.setVisible(False)
        self.ui.phone_number_error.setVisible(False)

        self.check_format()

        if self.ui.email_error.isVisible() or self.ui.phone_number_error.isVisible():
            return

        data = dict([
            ('first_name', self.ui.name.text()),
            ('second_name', self.ui.surname.text()),
            ('phone_number', self.ui.phone_number.text()),
            ('email', self.ui.email.text())
        ])
        msg = QMessageBox()
        if Database_Functional.get_instance(user_info.User.login).create_client(data):
            msg.setWindowTitle("Успех")
            msg.setText("Клиент успешно создан")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
        else:
            msg.setWindowTitle("Ошибка")
            msg.setText("Клиент не был создан")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()

    def check_format(self):
        if not (Lines_Parsing.check_email(self.ui.email.text())):
            self.ui.email_error.setText("Неверный формат почты")
            self.ui.email_error.setVisible(True)
        if not (Lines_Parsing.check_phone_number(self.ui.phone_number.text())):
            self.ui.phone_number.setText("Неверный формат номера телефона")
            self.ui.phone_number.setVisible(True)


class CarWindow(QWidget):
    def __init__(self):
        super(CarWindow, self).__init__()
        self.ui = Car_Widget.Ui_Form()
        self.ui.setupUi(self)

        self.init_ui()

    def init_ui(self):
        self.ui.addCarBtn.clicked.connect(self.addCar)
        self.ui.updateBtn.setIcon(QIcon('./sources/update_icon.png'))
        self.ui.updateBtn.clicked.connect(self.onUpdate)

        self.ui.label.setPixmap(QPixmap('./sources/icons8-tesla-model-x-64.png'))
        self.ui.clients.addItems(Database_Functional.get_instance(user_info.User.login).get_all_clients())

        self.ui.brand.setPlaceholderText('Введите бренд автомобиля')
        self.ui.model.setPlaceholderText('Введите модель автомобиля')
        self.ui.year.setPlaceholderText('Введите год выпуска автомобиля')
        self.ui.state_number.setPlaceholderText('Введите номер автомобиля')
        self.ui.technical_passport.setPlaceholderText('Введите тех паспорт автомобиля')

    def onUpdate(self):
        self.ui.clients.clear()
        self.ui.brand.clear()
        self.ui.model.clear()
        self.ui.technical_passport.clear()
        self.ui.year.clear()
        self.ui.state_number.clear()
        self.ui.clients.addItems(Database_Functional.get_instance(user_info.User.login).get_all_clients())

    def addCar(self):
        self.ui.state_error.setVisible(False)
        self.ui.passport_error.setVisible(False)

        self.check_format()
        if self.ui.state_error.isVisible() or self.ui.passport_error.isVisible():
            return

        msg = QMessageBox()
        data = dict([
            ('brand', self.ui.brand.text()),
            ('model', self.ui.model.text()),
            ('year', self.ui.year.text()),
            ('state', self.ui.state_number.text()),
            ('passport', self.ui.technical_passport.text()),
            ('client_email', self.ui.clients.currentText())
        ])
        if Database_Functional.get_instance(user_info.User.login).add_car(data):
            msg.setWindowTitle("Успех")
            msg.setText("Автомобиль успешно добавлен")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
        else:
            msg.setWindowTitle("Ошибка")
            msg.setText("Не удалось добавить автомобиль")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

    def check_format(self):
        if not (Lines_Parsing.check_state_number(self.ui.state_number.text())):
            self.ui.state_error.setText("Неверный формат номера авто")
            self.ui.state_error.setVisible(True)
        if not (Lines_Parsing.check_tech_passport(self.ui.technical_passport.text())):
            self.ui.passport_error.setText("Неверный формат тех паспорта")
            self.ui.passport_error.setVisible(True)


class CreateTaskWindow(QWidget):
    def __init__(self):
        super(CreateTaskWindow, self).__init__()
        self.ui = Tasks_Actions.Ui_Form()
        self.ui.setupUi(self)

        self.init_ui()

    def init_ui(self):
        self.ui.contractId.addItems(Database_Functional.get_instance(user_info.User.login).get_all_contacts_id())

        self.ui.authorLogin.setText(user_info.User.login)

        employees = Database_Functional.get_instance(user_info.User.login).get_all_workers()

        if len(employees) == 1:
            self.ui.executorLogin.addItem(employees[0])
        elif len(employees) > 1:
            self.ui.executorLogin.addItems(employees)

        self.ui.addBtn.clicked.connect(self.onAddTask)

    def onAddTask(self):
        data = dict([
            ('c_id', self.ui.contractId.currentText()),
            ('deadline', self.ui.deadlineDate.text()),
            ('auth_login', self.ui.authorLogin.text()),
            ('exec_login', self.ui.executorLogin.currentText())
        ])

        msg = QMessageBox()
        if Database_Functional.get_instance(user_info.User.login).add_task(data):
            msg.setWindowTitle("Успех")
            msg.setText("Задача успешно создана")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()
        else:
            msg.setWindowTitle("Ошибка")
            msg.setText("Задача не была создана")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()


class DisplayReport(QWidget):
    def __init__(self):
        super(DisplayReport, self).__init__()
        self.ui = Completed_Tasks_Widget.Ui_Form()

        self.layout = QVBoxLayout()
        self.ui.setupUi(self)

        self.init_ui()

    def init_ui(self):
        self.setLayout(self.layout)
        self.ui.updateBtn.clicked.connect(self.onUpdate)

        data = Database_Functional.get_instance(user_info.User.login).get_report()

        if data:
            self.ui.tableWidget = QTableWidget(len(data), len(data[0]))
        else:
            self.ui.tableWidget = QTableWidget()

        self.setup_table(data)

        self.ui.tableWidget.setHorizontalHeaderLabels(['Номер контракта', 'Дата создания задания',
                                                       'Дата выполнения задания', 'ID автора задания',
                                                       'ID исполнителя задания'])
        self.ui.tableWidget.resizeColumnsToContents()
        self.layout.addWidget(self.ui.tableWidget)
        self.layout.addWidget(self.ui.updateBtn)

    def setup_table(self, data):
        for row in range(len(data)):
            for col in range(len(data[row])):
                if isinstance(data[row][col], QDate):
                    data[row][col] = data[row][col].toString('MMMM d, yyyy')
                item = QTableWidgetItem(f"{data[row][col]}")
                self.ui.tableWidget.setItem(row, col, item)

    def onUpdate(self):
        self.ui.tableWidget.clearContents()
        new_data = Database_Functional.get_instance(user_info.User.login).get_report()
        self.ui.tableWidget.setRowCount(len(new_data))
        if new_data:
            self.setup_table(new_data)

