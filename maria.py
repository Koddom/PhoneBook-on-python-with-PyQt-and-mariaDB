import mariadb
import sys


DATABASE = 'phonebook'
CONN_PARAMS = None  # Определяется в функции first_connection()


class CursorDB:
    def __init__(self,):
        try:
            self.connection = mariadb.connect(**CONN_PARAMS)
        except mariadb.Error as e:
            print(f'Ошибка подключения к платформе MarinaDB: {e}')
            sys.exit(1)

        self.cursor = self.connection.cursor()
        self.cursor.execute('USE '+DATABASE)


def get_list_of_people(letters) -> list:
    """Отправляет запрос в БД и формирует выборку по первым буквам имени LIKE в letters"""

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


def get_list_of_birthday_people() -> list:
    """Возвращает список пользователей, чьё ДР выпадает на ближайшую неделю"""
    sql = "SELECT Name,Phone,DateBir,UserID FROM phonebook_data WHERE DateBir BETWEEN CURRENT_DATE() AND ADDDATE(CURRENT_DATE(), INTERVAL ? DAY)"
    data = (7,)
    gate = CursorDB()
    gate.cursor.execute(sql, data)
    selected = gate.cursor.fetchall()
    gate.cursor.close()
    gate.connection.close()

    return selected


def check_pass(login, password, remember_me) -> bool:
    """Проверяет правильность пары логин-пароль"""
    gate = CursorDB()
    gate.cursor.execute("SELECT Password,UserID FROM phonebook_data WHERE Name=?", (login,))
    user_password = gate.cursor.next()
    if not user_password:  # если запись запроса пустая т.е пользователя с таким именем нет в базе
        access = False
    elif user_password[0] == password:  # если пароль в выборке совпадает с введённым пользователем
        access = True
        if remember_me:
            # Для начала удаляем все другие отметки Remember_me
            gate.cursor.execute("UPDATE phonebook_data SET Remember_me=FALSE WHERE UserID IN( SELECT UserID FROM phonebook_data WHERE Remember_me=1)")
            # записываем отметку запомнить меня для автоматического заполнения полей авторизации
            gate.cursor.execute("UPDATE phonebook_data SET Remember_me=TRUE WHERE UserID=?", (user_password[1],))
        else:
            # или удаляем
            gate.cursor.execute("UPDATE phonebook_data SET Remember_me=False WHERE UserID=?", (user_password[1],))
        gate.connection.commit()
    else:  # иначе введён неправильный пароль
        access = False
    gate.cursor.close()
    gate.connection.close()
    return access


def add_new_entry_to_phonebook_data(name, password, date):
    gate = CursorDB()
    # Проверяем существует ли уже такая запись в телефонной книге
    gate.cursor.execute('SELECT * FROM phonebook_data WHERE Name=? AND Password=? AND DateBir=?', (name, password, date))
    if gate.cursor.next():
        print(f'Пользователь с именем {name}, и датой рождения {date} уже существует')
        return False
    else:
        try:  # Добавляем новую запись
            gate.cursor.execute('INSERT INTO phonebook_data(Name,Password,DateBir) VALUES (?,?,?)', (name, password, date))
            gate.connection.commit()
        except mariadb.Error as e:
            print(f'Не удалось добавить новую запись: {e}')

    gate.cursor.close()
    gate.connection.close()
    return True  # Возвращаем истину если успешно добавили пользователя в БД


def check_dublicate(cursor, row_data: tuple) -> bool:
    """Возвращает True если пользователя в БД с row_data не обнаружено
    row_data = (Name, Phone, DateBir)"""
    sql = 'SELECT Name, Phone, DateBir FROM phonebook_data WHERE Name=? AND Phone=? AND DateBir=?'
    cursor.execute(sql, row_data)
    if cursor.next():  # Если уже существует запись с подобными параметрами
        print('Нельзя изменить')
        return False
    else:
        return True


def update_entry(row_data, column) -> bool:
    """Меняет поле Name в таблице базы данных"""
    gate = CursorDB()
    if check_dublicate(gate.cursor, row_data[:-1]): # если дубликатов не обнаружено
        print('меняем запись')
        if column == 0:  # Если изменили колонку с именем
            field = 'Name'
        elif column == 1:  # изменили телефон
            field = 'Phone'
        elif column == 2:  # значит изменили дату
            field = 'DateBir'
        sql = f'UPDATE phonebook_data SET {field}=? WHERE UserID=?'
        data = (row_data[column], row_data[3])  # Получаем данные из нужной колонки, ID пользователя
        gate.cursor.execute(sql, data)
        gate.connection.commit()
        commit = True
    else:
        commit = False
    gate.cursor.close()
    gate.connection.close()
    return commit


def autologin():
    gate = CursorDB()
    # Проверяем нет ли галочки запомнить меня для автоматического входа
    gate.cursor.execute("SELECT Name,Password FROM phonebook_data WHERE UserID IN (SELECT UserID FROM auto_login)")
    user_exists = gate.cursor.next()
    if user_exists:
        login = user_exists[0]
        password = user_exists[1]
    else:
        login = ''
        password = ''
    gate.cursor.close()

    return login, password


def create_db(username_db, password):
    """Функция должна сработать только при первом запуске скрипта и создать необходимую базу данных
    с таблицей phonebook_data и пользователем admin pass"""
    conn_params = {
        'user': username_db,
        'password': password,
        'host': 'localhost',
        'database': ''
    }

    data = []  # формируем информацию  из people.csv для передачи в аргументы к SQL запросу и записи в базу данных.
    file = open('people.csv')
    for line in file:
        name_phone = line.split(',')
        name_phone[1] = name_phone[1].strip()
        data.append(tuple(name_phone))

    connection = mariadb.connect(**conn_params)
    cursor = connection.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS '+DATABASE)
    cursor.execute('USE '+DATABASE)
    print('База данных ' + DATABASE + ' создана')
    cursor.execute('CREATE TABLE IF NOT EXISTS phonebook_data('  # создаём основную таблицу для хранения информации
                        'UserID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,'
                        'Name VARCHAR(150) NOT NULL,'
                        'Password VARCHAR(100) NOT NULL DEFAULT "",'
                        'Phone VARCHAR(11),'
                        'DateBir DATE NOT NULL DEFAULT CURRENT_DATE(),'
                        'Remember_me BOOL NOT NULL DEFAULT 0)')
    cursor.execute("CREATE TABLE IF NOT EXISTS auto_login("  # вспомогательная таблица хранит пользователя с галочкой remember me
                   "N INT NOT NULL PRIMARY KEY AUTO_INCREMENT,"
                   "UserID INT)")
    connection.commit()
    cursor.execute("INSERT INTO phonebook_data (UserID,Name,Password,Phone,DateBir) VALUES (1,'admin','pass','','0001-01-01')")
    connection.commit()

    cursor.executemany("INSERT INTO phonebook_data (Name,Phone) VALUES (?,?)", data)
    cursor.execute("INSERT INTO auto_login (UserID)  VALUES (1)")

    connection.commit()
    cursor.close()
    connection.close()
    print('Таблица телефонных номеров создана. Для доступа используйте\nлогин admin\nпароль pass')


def first_connection():
    """Функция для проверки подключения к базе данных"""
    while True:  # Просим пользователя ввести логин пароль, пока не введёт верный. break строка в операторе try
        print('Пытаемся подключится к базе данных. Введите логин и пароль от mariaDB')
        username_db = 'egordmitriev'
        password = ''

        conn_params = {
            'user': username_db,
            'password': password,
            'host': 'localhost',  # !!!!! <-- указывай все настройки необходимые для подключения к бд
            'database': DATABASE
        }
        try:
            connection = mariadb.connect(**conn_params)
            connection.close()
            break # если полдключение удалось, то можно выйти из цикла попыток
        except mariadb.Error as e:
            if e.errno == 1044:  # Если введены неверный логин, пароль
                print('Доступ запрещён. Проверьте права пользователя', username_db)
                # далее просим заново ввести логин и парольћ
                continue
            elif e.errno == 1049:  # если база данных не найдена
                # создаём базу данных
                create_db(username_db, password)
                # connection = mariadb.connect(**conn_params)  # и подключаемся к базе данных
                break

    global CONN_PARAMS
    CONN_PARAMS = conn_params

