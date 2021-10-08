from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QCheckBox, QDateEdit
from PyQt5.QtCore import QSize, Qt, QRect, QDate
import sys
import maria


class Window(QMainWindow):  # Стартовое окно с вводом логина и пароля
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle('Авторизация')
        self.setGeometry(300, 300, 350, 300)

        self.username = QLineEdit(self)
        self.username.setGeometry(QRect(50, 10, 200, 21))
        self.username.setPlaceholderText('Логин')
        self.username.setClearButtonEnabled(True)
        self.username.setObjectName('Name')

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Пароль')
        self.password.setGeometry(QRect(50, 50, 200, 21))

        self.btn = QPushButton(self)
        self.btn.move(10, 150)
        self.btn.setText('Вход')
        self.btn.setFixedWidth(100)
        self.btn.clicked.connect(self.open_phonebook)

        self.btn1 = QPushButton(self)
        self.btn1.move(100, 150)
        self.btn1.setText('Регистрация')
        self.btn1.setFixedWidth(120)
        self.btn1.clicked.connect(self.registration)

        self.btn2 = QPushButton(self)
        self.btn2.move(220, 150)
        self.btn2.setText('Отмена')
        self.btn2.setFixedWidth(100)
        self.btn2.clicked.connect(self.exit)

        self.remember_me = QCheckBox('Запомнить меня')

        # вспомогательные строки чтобы каждый раз логин пароль не вводить
        self.password.setText('pass')
        self.username.setText('admin')

    def open_phonebook(self):
        if self.check_pass(self.username.text(), self.password.text()):
            self.window = TableWindow()
            self.window.show()
            self.close()
        else:
            print('пользователь с такими данными не найден')

    def check_pass(self, login, password):
        return maria.check_pass(login, password)


    def registration(self):
        self.window = RegistrationWindow()
        self.window.show()
        self.close()


    def exit(self):
        sys.exit()


class TableWindow(QMainWindow):
    def __init__(self):
        super(TableWindow, self).__init__()

        self.setMinimumSize(QSize(480, 600))
        self.setWindowTitle('Телефонная книга')

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.grid_layout = QGridLayout()
        central_widget.setLayout(self.grid_layout)
        self.table = QTableWidget(self)
        self.letters = 'аб'  # хранит буквы активной кнопки
        self.create_table()  # создание таблицы с выборкой из БД

        btn = QPushButton(self)
        self.grid_layout.addWidget(btn, 0, 0)

        self.create_alph_btn()

    def create_alph_btn(self):
        """ создаём кнопки бокового алфавита """
        self.btn1 = QPushButton(self)
        self.btn1.setText('АБ')
        self.btn1.clicked.connect(lambda: self.update_letter(self.btn1.text()))

        self.btn2 = QPushButton(self)
        self.btn2.setText('ВГ')
        self.btn2.clicked.connect(lambda: self.update_letter(self.btn2.text()))
        self.btn2.move(0, 21)

    def update_letter(self, letters):
        self.letters = letters  # сначала меняем свойство
        self.create_table()

    def create_table(self) -> None:
        """Формирует запрос в БД и заполняет таблицу данными выборки ФИО Телефон Дата"""
        selected = maria.get_list_of_people(self.letters)  # отправляем запрос в БД для получения выборки по буквам
        rows = selected.__len__()
        columns = 4
        self.table.setColumnCount(columns)
        self.table.setRowCount(rows)

        # Устанавливаем заголовки таблицы
        self.table.setHorizontalHeaderLabels(['Имя', 'Телефон', 'День рождения', 'ID'])

        # Устанавливаем выравнивание на заголовки
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
        self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignRight)

        # Заполняем каждую строку согласно полученной выборке selected
        for row in range(rows):
            for column in range(columns):
                self.table.setItem(row, column, QTableWidgetItem(str(selected[row][column])))

        self.table.hideColumn(3)  # скрываем 4-ю колонку в которой хранится ID. Мы его будем использовать при изменении записи
        # Делаем расайз колонок по содержимому
        self.table.resizeColumnsToContents()
        self.grid_layout.addWidget(self.table, 0, 1)  # Добавляем таблицу в сетку
        self.table.cellChanged[int,int].connect(self.changed_cell)

    def changed_cell(self, r, c):
        print(r,c)
        changed_data = self.table.item(r,c).text()  # получаем новые данные из колонки
        user_id = self.table.item(r,3).text()  # user_id находится в скрытой колонке
        if c == 0:  # если изменили имя
            maria.update_name(user_id, changed_data)
        elif c == 1:  # если поменяли телефон
            maria.update_phone(user_id, changed_data)
        elif c == 2:  # если изменили дату
            maria.update_datebir(user_id, changed_data)

        self.create_table()
        # data = [self.table.item(r, column) for column in range(self.table.columnCount()+1)]  # получаем данные ряда в котором были произведены изменения



    def change_table(self, letter):
        '''заменяет содержимое таблицы'''
        self.table.setItem(0, 0, QTableWidgetItem(letter))
        self.table.setItem(0, 1, QTableWidgetItem(letter))
        self.table.setItem(0, 2, QTableWidgetItem(letter))


class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Регистрация')
        self.setGeometry(300, 300, 300, 300)

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Имя Фамилия')
        self.username.setGeometry(50, 50, 200,21)

        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Пароль')
        self.password.setGeometry(50, 80, 200, 21)

        self.password1 = QLineEdit(self)
        self.password1.setPlaceholderText('Подтвердите пароль')
        self.password1.setGeometry(50, 110, 200, 21)

        self.date = QDateEdit(self)
        self.date.setGeometry(50, 150, 200, 21)
        self.date.setDate(QDate.currentDate())
        self.date.setCalendarPopup(True)

        self.ok_btn = QPushButton(self)
        self.ok_btn.move(50, 200)
        self.ok_btn.setFixedSize(95, 30)
        self.ok_btn.setText('OK')
        self.ok_btn.clicked.connect(self.ok)

        self.cancel_btn = QPushButton(self)
        self.cancel_btn.move(155, 200)
        self.cancel_btn.setFixedSize(95, 30)
        self.cancel_btn.setText('Отмена')
        self.cancel_btn.clicked.connect(self.back)

        self.username.setText('Иван')
        self.password.setText('1234')
        self.password1.setText('1234')


    def ok(self):
        print('Записать в БД')
        name = self.username.text()
        password = self.password.text()
        date = self.date.text().split('/')  # преобразуем дату в формат строки для DB
        date.reverse()
        date = '-'.join(date)
        if maria.add_new_entry_to_phonebook_data(name,password,date):
            self.open_phonebook()

    def open_phonebook(self):
        self.window = TableWindow()
        self.window.show()
        self.close()


    def back(self):
        print('вернуться назад')
        self.window = Window()
        self.window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

