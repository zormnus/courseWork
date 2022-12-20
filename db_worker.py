import logging

import bcrypt
from PyQt6.QtSql import QSqlQuery, QSqlDatabase
from config import sql_driver, host_name, db_name, db_password

logging.basicConfig(filename='logs.txt', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def encode(text: str) -> str:
    return bcrypt.hashpw(text.encode(), bcrypt.gensalt()).decode()


class db_worker:
    def __init__(self, user_name):
        self.database = QSqlDatabase.addDatabase(sql_driver)
        self.database.setHostName(host_name)
        self.database.setUserName(user_name)
        self.database.setDatabaseName(db_name)
        self.database.setPassword(db_password)

        self.create_session(user_name)

        if self.database.open():
            logging.info('Соединение с базой данных успешно установлено')
        else:
            logging.critical(f'Ошибка соединения с базой данных: {self.database.lastError().text()}')
            self.database = None

    @staticmethod
    def create_session(user_name):
        query = QSqlQuery()
        text = f"SET SESSION AUTHORIZATION {user_name}"
        if not(query.exec(text)):
            print(query.lastError().text())

    @staticmethod
    def get_UserId_by_login(login):
        query = QSqlQuery()

        if not (query.exec(f"SELECT Employee_id FROM Employee WHERE Login='{login}'")):
            print(query.lastError().text())
        query.first()
        return query.value(0)

    @staticmethod
    def get_UserPos_by_login(login) -> int:
        query = QSqlQuery()
        if not (query.exec(f"SELECT * FROM get_position('{login}')")):
            print(query.lastError().text())
        query.first()
        return query.value(0)

    @staticmethod
    def check_user(login, password) -> bool:
        query = QSqlQuery()

        query.exec(f"SELECT * FROM get_password('{login}')")
        query.first()
        from_db_password = str(query.value(0))

        if from_db_password == '':
            return False

        if bcrypt.checkpw(password.encode(), from_db_password.encode()):
            return True
        return False

    def user_authorization(self, login, password) -> bool:
        if self.check_user(login, password):
            logging.info('Успешная авторизация!')
            return True
        logging.warning('Введены несуществующий логин и/или пароль!')
        return False

    @staticmethod
    def user_registration(user_data) -> bool:
        user_data['password'] = encode(user_data['password'])

        query = QSqlQuery()
        check_login_query = f"SELECT * FROM Employee WHERE Login='{user_data['login']}'"
        query.exec(check_login_query)
        query.first()

        if query.size() > 0:
            return False

        query.clear()

        create_employee_query = f"CALL create_employee(" \
                                f"'{user_data['first_name']}', '{user_data['last_name']}', '{user_data['email']}'," \
                                f"'{user_data['phone_number']}', {user_data['position']}, '{user_data['login']}'," \
                                f"'{user_data['password']}')"
        query.exec(create_employee_query)
        return True

    def get_data(self, user_id, with_prepare=False):
        query = QSqlQuery()
        text = f"SELECT Task_id,Contract_id,Creation_date,Completion_date,Deadline_date,Status,Author_id" \
               f" FROM task WHERE executor_id = {user_id}"
        query.exec(text)
        return self.prepareData(query)

    @staticmethod
    def get_task_ids(user_id):
        query = QSqlQuery()
        text = f"SELECT Task_id FROM Task WHERE Executor_id={user_id}"
        query.exec(text)

        result = []

        while query.next():
            result.append(query.value('task_id'))
        return result

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
    def create_user(user_name, position):
        query = QSqlQuery()
        role = "service_station_admin" if position == 1 else "mechanic" \
            if position == 2 else "accountant"
        text = f"CREATE USER {user_name} IN ROLE {role}"
        query.exec(text)
        logging.info(f"user {user_name} in role {role} was created!")

    @staticmethod
    def get_task_text(task_id):
        query = QSqlQuery()
        text = f"SELECT * FROM get_task_text({task_id})"
        query.exec(text)
        query.first()
        return str(query.value(0))

    @staticmethod
    def update_task_status(task_id):
        query = QSqlQuery()
        text = f"CALL update_task_status({task_id})"
        query.exec(text)

    @staticmethod
    def get_authorName(author_id):
        query = QSqlQuery()
        text = f"SELECT * FROM get_author_fullName({author_id})"
        query.exec(text)
        query.first()

        res = f"{query.value(0)} {query.value(1)}"
        return res

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
