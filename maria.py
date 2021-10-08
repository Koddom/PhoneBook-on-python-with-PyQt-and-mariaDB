import mariadb
import sys


FIRST_LAUNCH = True


class CursorDB:
    def __init__(self):
        try:
            # connection parameters
            conn_params = {
                "user": "egordmitriev",
                "password": "",
                "host": "localhost",
                "database": ""
            }
            self.connection = mariadb.connect(**conn_params)
        except mariadb.Error as e:
            print(f'Ошибка подключения к платформе MarinaDB: {e}')
            sys.exit(1)

        self.cursor = self.connection.cursor()
        self.cursor.execute('USE phonebook')

    def create_phonebook_data(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS phonebook_data('
                            'UserID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,'
                            'Name VARCHAR(150) NOT NULL,'
                            'Password VARCHAR(100) NOT NULL,'
                            'Phone VARCHAR(11),'
                            'DateBir DATE NOT NULL,'
                            'Remember_me BOOL NOT NULL DEFAULT 0)')
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
        print('Таблица телефонных номеров создана')


def get_list_of_people(letters) -> list:
    """Отправляет запрос в БД и формирует выборку по буквам первым буквам имени LIKE в letters"""

    # Сначала из всех букв letters получаем большие и маленькие, и формируем из них кортеж данных
    data = []
    for letter in letters.lower():
        data.append(letter+'%')
        data.append(letter.upper()+'%')
    data = tuple(data)  # data = ('а%', 'А%', 'б%', 'Б%')
    # потом пишем начальную строчку запроса и приклеиваем к ней ещё строки фильтрации(кол-во зависит от len(letters)).
    sql = 'SELECT Name,Phone,DateBir,UserID FROM phonebook_data WHERE Name LIKE ?'
    for l in range(len(data)-1):  # количество конкатенаций должно быть на 1 меньше количества параметров запроса
        sql += ' OR Name LIKE ?'

    gate = CursorDB()
    gate.cursor.execute(sql, data)
    selected = gate.cursor.fetchall()
    gate.cursor.close()
    gate.connection.close()

    return selected


def check_pass(login, password) -> bool:
    """Проверят правильность пары логин-пароль"""
    gate = CursorDB()
    gate.cursor.execute("SELECT Password FROM users WHERE Login=?", (login,))
    user_password = gate.cursor.next()
    if not user_password:  # если запись запроса пустая т.е пользователя с таким именем нет в базе
        return False
    elif user_password[0] == password:  # если пароль в выборке совпадает с введённым пользователем
        return True
    else:
        return False


def add_new_entry_to_phonebook_data(name, password, date):
    gate = CursorDB()
    # Проверяем существует ли уже такая запись в телефонной книге
    gate.cursor.execute('SELECT * FROM phonebook_data WHERE Name=? AND Password=? AND DateBir=?', (name, password, date))
    if gate.cursor.next():
        print(f'Пользователь с именем {name}, и датой рождения {date} уже существует')
        return False 
    else:
        try:  # Добавляем новую запись
            cursor.cursor.execute('INSERT INTO phonebook_data(Name,Password,DateBir) VALUES (?,?,?)', (name, password, date))
            cursor.connection.commit()
        except mariadb.Error as e:
            print(f'Не удалось добавить новую запись: {e}')

    cursor.cursor.close()
    cursor.connection.close()
    return True  # Возвращаем истину если успешно добавили пользователя в БД


def update_name(user_id, changed_data) -> None:
    """Меняет поле Name в таблице базы данных"""
    gate = CursorDB()
    sql = 'UPDATE phonebook_data SET Name=? WHERE UserID=?'
    data = (changed_data, user_id)
    gate.cursor.execute(sql, data)
    gate.connection.commit()
    gate.cursor.close()
    gate.connection.close()


def update_phone(user_id, changed_data):
    """Меняет поле Phone в таблице базы данных"""
    gate = CursorDB()
    sql = 'UPDATE phonebook_data SET Phone=? WHERE UserID=?'
    data = (changed_data, user_id)
    gate.cursor.execute(sql, data)
    gate.connection.commit()
    gate.cursor.close()
    gate.connection.close()


def update_datebir(user_id, changed_data):
    gate = CursorDB()
    try:
        sql = 'UPDATE phonebook_data SET DateBir=? WHERE UserID=?'
        data = (changed_data, user_id)
        gate.cursor.execute(sql, data)
        gate.connection.commit()
    except mariadb.Error as e:
        print(f'Ошибка обновления даты: {e}')
    gate.cursor.close()
    gate.connection.close()


if FIRST_LAUNCH:
    cursor = CursorDB()
    cursor.create_phonebook_data()
    FIRST_LAUNCH = False

# cursor.execute('CREATE DATABASE IF NOT EXISTS phonebook')
# cursor.execute('USE phonebook')
# cursor.execute('CREATE TABLE IF NOT EXISTS users('
#                'UserID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,'
#                'Login VARCHAR(100) NOT NULL,'
#                'Password VARCHAR(100) NOT NULL)')
# try:
#     cursor.execute("INSERT INTO users(UserID, Login, Password) VALUES (1,'admin','pass')")
# except mariadb.Error as e:
#     print('Duplicate entry' in str(e))
#     print(f'ошибка создания пользователя admin: {e}')
# connection.commit()
# cursor.close()
# connection.close()
