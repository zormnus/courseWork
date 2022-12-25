import logging

from PyQt6.QtSql import QSqlQuery, QSqlDatabase, QSql
from config import Config

logging.basicConfig(filename='logs.txt', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


class db_worker:
    def __init__(self, user_name):
        self.database = QSqlDatabase.addDatabase(Config.sql_driver)
        self.database.setHostName(Config.host_name)
        self.database.setDatabaseName(Config.db_name)
        if user_name == 'postgres':
            self.database.setUserName("postgres")
            self.database.setPassword("Admin1010")
        else:
            self.database.setUserName(Config.user_name)
            self.database.setPassword(Config.db_password)

        if self.database.open():
            logging.info(f'Соединение с базой данных пользователя {user_name} успешно установлено')
        else:
            logging.critical(
                f'Ошибка соединения с базой данных пользователя {user_name}: {self.database.lastError().text()}')
            self.database = None

    @staticmethod
    def get_UserId_by_login(login):
        query = QSqlQuery()
        query.prepare("SELECT Employee_id FROM Employee WHERE Login=?")
        query.addBindValue(login)
        if not (query.exec()):
            logging.critical(query.lastError().text())
            return
        query.first()
        return query.value(0)

    @staticmethod
    def get_UserPos_by_login(login) -> int:
        query = QSqlQuery()
        query.prepare("SELECT * FROM get_position(?)")
        query.addBindValue(login)
        if not (query.exec()):
            logging.critical(query.lastError().text())
            return None
        query.first()
        return query.value(0)

    @staticmethod
    def check_user(login, password) -> bool:
        query = QSqlQuery()
        query.prepare("SELECT * FROM check_user(?,?)")

        query.addBindValue(login)
        query.addBindValue(password)

        if not (query.exec()):
            logging.critical(query.lastError().text())
            return False
        query.first()
        return query.value(0)

    def user_registration(self, user_data) -> bool:
        query = QSqlQuery(self.database)

        if not (query.exec(f"CALL create_employee('{user_data['first_name']}', '{user_data['last_name']}', "
                           f"'{user_data['email']}', '{user_data['phone_number']}', {user_data['position']},"
                           f"'{user_data['login']}', '{user_data['password']}', '{user_data['car_service_name']}')")):
            logging.critical(query.lastError().text())
            return False
        return True

    def get_car_service_name(self, login):
        query = QSqlQuery()
        query.prepare("SELECT Name FROM Car_service WHERE Car_service_id="
                      "(SELECT Car_service_id FROM Employee WHERE Login=?)")
        query.addBindValue(login)

        if not (query.exec()):
            logging.critical(query.lastError().text())
        query.first()
        return query.value(0)


    def get_data(self, user_id):
        query = QSqlQuery()

        query.prepare("SELECT Task_id,Contract_id,Creation_date,Completion_date,"
                      "Deadline_date,Status,Author_id FROM task WHERE executor_id = ?")

        query.addBindValue(user_id)

        if not (query.exec()):
            logging.critical(query.lastError().text())
            return None
        return self.prepareData(query)

    @staticmethod
    def prepareData(query: QSqlQuery) -> list:
        result = []
        it = 0
        rec = query.record()
        while query.next():
            result.append([])
            for i in range(rec.count()):
                val = query.value(i)
                result[it].append(val)
            it += 1
        return result

    @staticmethod
    def get_all_clients():
        query = QSqlQuery()

        if not (query.exec("SELECT * FROM get_all_clients()")):
            logging.critical(query.lastError().text())
            return None

        result = []
        while query.next():
            result.append(query.value(0))
        return result

    def get_report(self):
        query = QSqlQuery()

        query.prepare("SELECT * FROM completed_tasks")

        if not (query.exec()):
            logging.critical(query.lastError().text())

        return self.prepareData(query)

    def get_all_services(self):
        query = QSqlQuery()

        if not (query.exec("SELECT * FROM get_all_services()")):
            logging.critical(query.lastError().text())
            return None

        return self.prepare_data(query)

    def get_all_car_services(self):
        query = QSqlQuery()

        if not (query.exec("SELECT * FROM get_all_car_services()")):
            logging.critical(query.lastError().text())
            return None

        return self.prepare_data(query)

    def get_all_technical_passports(self):
        query = QSqlQuery()
        if not (query.exec("SELECT * FROM get_all_technical_passports()")):
            logging.critical(query.lastError().text())
            return None

        return self.prepare_data(query)

    def get_all_autoparts(self):
        query = QSqlQuery()
        if not (query.exec("SELECT * FROM get_all_autoparts()")):
            logging.critical(query.lastError().text())
            return None
        return self.prepare_data(query)

    @staticmethod
    def prepare_data(query):
        result = dict()
        while query.next():
            result[query.value(1)] = query.value(0)
        return result

    @staticmethod
    def create_contract(data: dict) -> bool:
        query = QSqlQuery()

        if not (query.exec(f"CALL create_contract('{data['cs_name']}',"
                           f"'{data['cl_email']}',"
                           f"'{data['passport']}',"
                           f"'{data['service']}',"
                           f"'{data['part']}')")):
            logging.critical(query.lastError().text())
            return False
        logging.info('contract was created!')
        return True

    @staticmethod
    def get_task_text(task_id):
        query = QSqlQuery()

        query.prepare("SELECT * FROM get_task_text(?)")

        query.addBindValue(task_id)
        if not (query.exec()):
            logging.critical(query.lastError().text())

        query.first()
        return query.value(0)

    @staticmethod
    def update_task_status(contract_id):
        query = QSqlQuery()

        if not (query.exec(f"CALL update_task_status({contract_id})")):
            logging.critical(query.lastError().text())

    @staticmethod
    def get_authorLogin(author_id):
        query = QSqlQuery()
        query.prepare("SELECT * FROM get_author_Login(?)")

        query.addBindValue(author_id)

        if not (query.exec()):
            logging.critical(query.lastError().text())
        query.first()

        return query.value(0)

    @staticmethod
    def get_all_workers() -> list:
        query = QSqlQuery()
        query.prepare("SELECT * FROM get_all_workers()")

        if not (query.exec()):
            logging.critical(query.lastError().text())
            return []

        result = []

        while query.next():
            result.append(query.value(0))
        return result

    @staticmethod
    def get_all_contacts_id() -> list:
        query = QSqlQuery()
        query.prepare("SELECT * FROM get_all_contacts_id()")

        if not (query.exec()):
            logging.critical(query.lastError().text())
            return []

        result = []
        while query.next():
            result.append(str(query.value(0)))
        return result

    @staticmethod
    def create_client(data: dict) -> bool:
        query = QSqlQuery()

        if not (query.exec(f"CALL create_client('{data['first_name']}', '{data['second_name']}', "
                           f"'{data['phone_number']}', '{data['email']}')")):
            logging.critical(query.lastError().text())
            return False

        logging.info(f"client {data['first_name']} {data['second_name']} was created!")
        return True

    @staticmethod
    def add_car(data: dict) -> bool:
        query = QSqlQuery()
        if not (query.exec(f"CALL create_car('{data['brand']}', '{data['model']}', '{data['year']}',"
                           f"'{data['state']}', '{data['passport']}', '{data['client_email']}')")):
            logging.critical(query.lastError().text())
            return False
        logging.info(f"car {data['state']} was created!")
        return True

    @staticmethod
    def add_task(data: dict) -> bool:
        query = QSqlQuery()

        if not (query.exec(f"CALL create_task({data['c_id']}, '{data['deadline']}', "
                           f"'{data['auth_login']}', '{data['exec_login']}')")):
            logging.critical(query.lastError().text())
            return False
        logging.info(f"task with contract id = {data['c_id']} was created!")
        return True

    def __del__(self):
        self.database.close()


class Database_Functional:
    _instance = None
    user_name = None

    @staticmethod
    def get_instance(user_name=None):
        if Database_Functional._instance is None or Database_Functional.user_name != user_name:
            Database_Functional._instance = db_worker(user_name)
            Database_Functional.user_name = user_name
        return Database_Functional._instance
