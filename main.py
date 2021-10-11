from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QGridLayout, QTableWidget, \
    QTableWidgetItem, QLineEdit, QCheckBox, QDateEdit, QVBoxLayout, QMessageBox, QButtonGroup
from PyQt5.QtCore import QSize, Qt, QDate
import sys
import maria


class Window(QMainWindow):  # Стартовое окно с вводом логина и пароля
    def __init__(self, auto_login: bool):
        super(Window, self).__init__()
        self.setWindowTitle('Авторизация')
        self.setGeometry(300, 300, 350, 300)

        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Логин')
        self.username.setClearButtonEnabled(True)
        self.username.setObjectName('Name')

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText('Пароль')

        self.btn = QPushButton(self)
        self.btn.setText('Вход')
        self.btn.setFixedWidth(100)
        self.btn.clicked.connect(self.open_phonebook)

        self.btn1 = QPushButton(self)
        self.btn1.setText('Регистрация')
        self.btn1.setFixedWidth(120)
        self.btn1.clicked.connect(self.registration)

        self.btn2 = QPushButton(self)
        self.btn2.setText('Отмена')
        self.btn2.setFixedWidth(100)
        self.btn2.clicked.connect(self.exit)

        login, password = maria.autologin()
        self.remember_me = QCheckBox('Запомнить меня')

        self.show_pass = QCheckBox('Показать пароль')
        self.show_pass.toggled.connect(self.show_password)


        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        v_layout = QVBoxLayout()
        v_layout.addSpacing(1)
        v_layout.addWidget(self.username)
        v_layout.addWidget(self.password)
        v_layout.addWidget(self.btn)
        v_layout.addWidget(self.btn1)
        v_layout.addWidget(self.btn2)
        v_layout.addWidget(self.remember_me)
        v_layout.addWidget(self.show_pass)
        central_widget.setLayout(v_layout)

        if login != '':
            # self.remember_me.setChecked(True)
            self.username.setText(login)
            self.password.setText(password)
        if auto_login:
            self.open_phonebook()
        else:
            self.show()

    def show_password(self):
        if self.show_pass.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def open_phonebook(self):
        if maria.check_pass(self.username.text(), self.password.text(),self.remember_me.isChecked()):
            self.window = TableWindow()
            self.window.show()
            self.close()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка авторизации")
            msg.setText("пользователь с такими данными не найден")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def registration(self):
        self.window = RegistrationWindow()
        self.window.show()
        self.close()

    def exit(self):
        sys.exit()


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


class TableWindow(QMainWindow):
    def __init__(self):
        super(TableWindow, self).__init__()

        self.setMinimumSize(QSize(480, 600))
        self.setWindowTitle('Дни рождения на ближайшую неделю')

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.grid_layout = QGridLayout()
        central_widget.setLayout(self.grid_layout)

        self.letters = ''  # хранит буквы активной кнопки, если букв нет, будет показан список ДР
        self.create_table()  # создание таблицы с выборкой из БД

        btn = QPushButton(self)
        btn.setText('exit')
        btn.clicked.connect(self.logout)
        self.grid_layout.addWidget(btn, 1, 0)

        btn_delete = QPushButton(self)
        btn_delete.setText('-')
        # btn.clicked.connect(self.delete_user)
        self.grid_layout.addWidget(btn_delete, 1, 1)

        self.buttons = []
        self.generate_alphas()

        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)
        for button in self.buttons:
            self.btn_grp.addButton(button)
        self.btn_grp.buttonClicked.connect(self.letters_click)

    def generate_alphas(self) -> None:
        letters = ['АБ','ВГ','ДЕ','ЖЗИЙ','КЛ','МН','ОП','РС','ТУ','ФХ','ЦЧШЩ','ЪЫЬЭ','ЮЯ']
        for i in letters:
            btn = QPushButton(self)
            btn.setText(i)
            self.v_layout.addWidget(btn)
            self.buttons.append(btn);

    def letters_click(self, btn) -> None :
        """меняет свойство активных букв"""
        self.letters = btn.text()  # сначала меняем свойство
        self.create_table()  # потом обновляем таблицу

    def create_table(self) -> None:
        """Формирует запрос в БД и заполняет таблицу данными выборки ФИО Телефон Дата"""
        self.table = QTableWidget(self)
        if self.letters != '':
            selected = maria.get_list_of_people(self.letters)  # отправляем запрос в БД для получения выборки по буквам
            self.setWindowTitle('Телефонная книга')
        else:
            selected = maria.get_list_of_birthday_people()
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
        # self.table.resizeColumnsToContents()

        self.v_layout = QVBoxLayout()
        self.v_layout.setAlignment(Qt.AlignTop)

        self.grid_layout.addLayout(self.v_layout, 0, 0)
        self.grid_layout.addWidget(self.table, 0, 1)  # Добавляем таблицу в сетку
        self.table.cellChanged[int,int].connect(self.changed_cell)  # если пользователь отредактировал запись

    def changed_cell(self, r, c):
        # print(r, c)
        # changed_data = self.table.item(r, c).text()  # получаем новые данные из колонки
        row_data = [str(self.table.item(r, column).text()) for column in range(self.table.columnCount())]  # получаем данные ряда в котором были произведены изменения
        row_data = tuple(row_data)
        user_id = self.table.item(r, 3).text()  # user_id находится в скрытой колонке
        if maria.update_entry(row_data, c):
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка изменения данных")
            msg.setText("Запись успешно изменена")
            # msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            print('')
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка изменения данных")
            msg.setText("Такой пользователь уже существует")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        self.create_table()

    def logout(self):
        self.window = Window(False)
        self.close()

    # def change_table(self, letter):
    #     '''заменяет содержимое таблицы'''
    #     self.table.setItem(0, 0, QTableWidgetItem(letter))
    #     self.table.setItem(0, 1, QTableWidgetItem(letter))
    #     self.table.setItem(0, 2, QTableWidgetItem(letter))


def main():
    maria.first_connection()  # проверяем подключение к базе
    app = QApplication(sys.argv)
    window = Window(False)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

