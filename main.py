import random
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QInputDialog
from PyQt6.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import QSize, QDateTime
import sqlite3
import csv


def make_menu(self):
    """ Функция создания главного меню """
    global menu
    self.deleteLater()
    menu.show()


class Game(QWidget):  # класс самой игры
    def __init__(self):
        super().__init__()
        global menu

        self.setWindowTitle('Фортуна, на память')  # название игры
        self.setGeometry(0, 0, 480, 480)
        self.setFixedSize(480, 480)

        self.login = QLabel(self)  # текст говорящий об уровне сложности
        self.login.setText(f'Уровень игры: {menu.mode_tx}')
        self.login.resize(290, 25)
        self.login.move(100, 0)
        self.login.setFont(QFont('Times', 20))

        self.cor_posled = []
        self.posled = []

        mas = ['Red', 'Green', 'Blue', 'Yellow', 'Purple', 'Orange']
        con = sqlite3.connect('db_files/levels.db')
        cur = con.cursor()
        if menu.mode_tx == 'Easy':  # получение цветов (колличество которых зависит от уровня сложности)
            name1 = mas[random.randint(0, 5)]
            name2 = mas[random.randint(0, 5)]
            while name1 == name2:
                name2 = mas[random.randint(0, 5)]
            self.color1, self.color2 = cur.execute(f"""SELECT color_off, color_on FROM levels
            WHERE name = '{name1}' OR name = '{name2}'""").fetchall()
        elif menu.mode_tx == 'Medium':
            name1 = mas[random.randint(0, 5)]
            name2 = mas[random.randint(0, 5)]
            name3 = mas[random.randint(0, 5)]
            name4 = mas[random.randint(0, 5)]
            while len(set([name1, name2, name3, name4])) != len([name1, name2, name3, name4]):
                name2 = mas[random.randint(0, 5)]
                name3 = mas[random.randint(0, 5)]
                name4 = mas[random.randint(0, 5)]
            self.color1, self.color2, self.color3, self.color4 = cur.execute(f"""SELECT color_off, color_on FROM levels
WHERE name = '{name1}' OR name = '{name2}' OR name = '{name3}' OR name = '{name4}'""").fetchall()
        else:
            colors = [list(i) for i in cur.execute("SELECT color_off, color_on FROM levels").fetchall()]
            random.shuffle(colors)
            self.color1, self.color2, self.color3, self.color4, self.color5, self.color6 = colors
        cur.close()

        self.do_paint = False
        self.do_paint_start = True
        self.update()
        self.make_posled()

    def make_posled(self):
        """ Добавления сектора в зависимости от уровня сложности """
        if menu.mode_tx == 'Easy':
            self.cor_posled.append(random.randint(0, 1))
        elif menu.mode_tx == 'Medium':
            self.cor_posled.append(random.randint(0, 3))
        else:
            self.cor_posled.append(random.randint(0, 5))
        self.do_paint = True
        self.inx = self.cor_posled[-1]
        self.mode = False
        self.update()
        self.posled = []

    def proba(self):
        """ Функция костылик нужная для отсчета секунды изменения цвета """
        time = QDateTime.currentDateTime().addSecs(1)
        while QDateTime.currentDateTime() < time:
            pass
        self.mode = True
        self.update()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """ Функция дял отслеживания мышки, а точнее нажатия и координат для определения сектора """
        if (event.pos().x() - 230) ** 2 + (event.pos().y() - 220) ** 2 <= 150 ** 2:  # Проверка на нахождение мышки в кругу
            if menu.mode_tx == 'Easy':  # Определение секторов по координатам мышки
                if event.pos().x() == 230:
                    return
                elif event.pos().x() > 230:
                    i = 1
                else:
                    i = 0
            elif menu.mode_tx == 'Medium':
                if event.pos().x() == 230 or event.pos().y() == 220:
                    return
                elif event.pos().x() > 230 and event.pos().y() > 220:
                    i = 3
                elif event.pos().x() < 230 and event.pos().y() > 220:
                    i = 2
                elif event.pos().x() < 230 and event.pos().y() < 220:
                    i = 1
                else:
                    i = 0
            else:
                if event.pos().x() == 230 or event.pos().y() == 220 or \
                   (event.pos().x() - 230) * 3 ** 0.5 == (event.pos().y() - 220) or \
                   (event.pos().x() - 230) * 3 ** 0.5 == -(event.pos().y() - 220):
                    return
                elif event.pos().y() < 220 and -(event.pos().x() - 230) * 3 ** 0.5 < (event.pos().y() - 220):
                    i = 0
                elif -(event.pos().x() - 230) * 3 ** 0.5 > (event.pos().y() - 220) and \
                      (event.pos().x() - 230) * 3 ** 0.5 > (event.pos().y() - 220):
                    i = 1
                elif event.pos().y() < 220 and (event.pos().x() - 230) * 3 ** 0.5 < (event.pos().y() - 220):
                    i = 2
                elif event.pos().y() > 220 and -(event.pos().x() - 230) * 3 ** 0.5 > (event.pos().y() - 220):
                    i = 3
                elif -(event.pos().x() - 230) * 3 ** 0.5 < (event.pos().y() - 220) and \
                      (event.pos().x() - 230) * 3 ** 0.5 < (event.pos().y() - 220):
                    i = 4
                elif event.pos().y() > 220 and (event.pos().x() - 230) * 3 ** 0.5 > (event.pos().y() - 220):
                    i = 5
            self.posled.append(i)  # Добовление сектора (выбранного пользователем) в последовательность (пользователя)
            if self.posled != self.cor_posled[:len(self.posled)]:  # Сравнение последовательностей, а именно проверка что пользователь правильно нажал на сектор
                self.setMouseTracking(False)  # Остановка слежения за мышкой
                return self.end()  # Переход в функцию завершения игры
            elif self.posled == self.cor_posled:  # Проверка что пользователь полностью повторил комбинацию
                self.make_posled()

    def paintEvent(self, event):
        """ Функция разрешающая рисовать в окне """
        if self.do_paint:  # Проверка нужно ли что-то перерисовывать
            painter = QPainter()  # Создаём экземпляр класса
            painter.begin(self)  # Автивируем режим рисования
            if self.do_paint_start:  # Проверяем рисует ли программа начальный круг или изменяет цвета секторов
                if menu.mode_tx == 'Easy':  # Рисуем количество секторов в зависимости от уровня сложности
                    i = 90
                    for color in (self.color1[0], self.color2[0]):
                        painter.setBrush(QBrush(QColor(color)))
                        painter.drawPie(80, 70, 300, 300, i * 16, 180 * 16)
                        i += 180
                elif menu.mode_tx == 'Medium':
                    i = 0
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0]):
                        painter.setBrush(QBrush(QColor(color)))
                        painter.drawPie(80, 70, 300, 300, i * 16, 90 * 16)
                        i += 90
                else:
                    i = 0
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0],
                                  self.color5[0], self.color6[0]):
                        painter.setBrush(QBrush(QColor(color)))
                        painter.drawPie(80, 70, 300, 300, i * 16, 60 * 16)
                        i += 60
                self.do_paint_start = False  # Выключаем возможность рисовать круг полностью заново
            else:
                if menu.mode_tx == 'Easy':  # выделяем сектор в зависимости от уровня сложности
                    j1 = [90, 270][self.inx]
                    color1 = [self.color1, self.color2][self.inx]
                    j = 90
                    for color in (self.color1[0], self.color2[0]):
                        if color != color1[0]:
                            painter.setBrush(QBrush(QColor(color)))
                        else:
                            painter.setBrush(QBrush(QColor(color1[1])))
                        painter.drawPie(80, 70, 300, 300, j * 16, 180 * 16)
                        j += 180
                    if self.mode:
                        painter.setBrush(QBrush(QColor(color1[0])))
                        painter.drawPie(80, 70, 300, 300, j1 * 16, 180 * 16)
                elif menu.mode_tx == 'Medium':
                    j1 = [0, 90, 180, 270][self.inx]
                    color1 = [self.color1, self.color2, self.color3, self.color4][self.inx]
                    j = 0
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0]):
                        if color != color1[0]:
                            painter.setBrush(QBrush(QColor(color)))
                        else:
                            painter.setBrush(QBrush(QColor(color1[1])))
                        painter.drawPie(80, 70, 300, 300, j * 16, 90 * 16)
                        j += 90
                    if self.mode:
                        painter.setBrush(QBrush(QColor(color1[0])))
                        painter.drawPie(80, 70, 300, 300, j1 * 16, 90 * 16)
                else:
                    j1 = [0, 60, 120, 180, 240, 300][self.inx]
                    color1 = [self.color1, self.color2, self.color3, self.color4, self.color5, self.color6][self.inx]
                    j = 0
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0],
                                  self.color5[0], self.color6[0]):
                        if color != color1[0]:
                            painter.setBrush(QBrush(QColor(color)))
                        else:
                            painter.setBrush(QBrush(QColor(color1[1])))
                        painter.drawPie(80, 70, 300, 300, j * 16, 60 * 16)
                        j += 60
                    if self.mode:
                        painter.setBrush(QBrush(QColor(color1[0])))
                        painter.drawPie(80, 70, 300, 300, j1 * 16, 60 * 16)
                self.proba()  # Вызов функции-костылика-таймера
            painter.end()  # Деактивируем режим рисования

    def end(self):
        """ Функция окончания игры """
        global menu

        con = sqlite3.connect('db_files/gamers.db')  # запись результата в db таблицу
        cur = con.cursor()
        mas1 = ['Easy', 'Medium', 'Hard']
        mas2 = ['result_easy', 'result_medium', 'result_insame']
        mode = mas2[mas1.index(menu.mode_tx)]
        schet = cur.execute(f"""SELECT {mode} FROM users
                                              WHERE userid = '{menu.id}'""").fetchall()
        cur.execute(f"""UPDATE users SET {mode} = '{max(schet[0][0], len(self.cor_posled) - 1)}'
                        WHERE userid = '{menu.id}'""").fetchall()
        con.commit()

        btn_menu = QPushButton('Menu', self)  # выход в меню
        btn_menu.move(130, 200)
        btn_menu.resize(200, 60)
        btn_menu.setFont(QFont('Times', 25))
        btn_menu.show()

        btn_new_game = QPushButton('Again', self)  # ещё игра
        btn_new_game.move(130, 300)
        btn_new_game.resize(200, 60)
        btn_new_game.setFont(QFont('Times', 25))
        btn_new_game.show()

        btn_menu.clicked.connect(lambda x: make_menu(self))  # выход в меню
        btn_new_game.clicked.connect(self.new_game)  # создание новой игры

    def new_game(self):
        """ Функция создания новой игры """
        global game

        self.deleteLater()  # уничтожение прошлой игры

        game = Game()  # создание новой игры
        game.show()


class Menu(QWidget):  # класс меню
    def __init__(self):
        super().__init__()
        self.reg()
        self.setGeometry(0, 0, 600, 500)

        con = sqlite3.connect('db_files/gamers.db')  # Создание базы данных
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                userid        INTEGER PRIMARY KEY,
                login         TEXT,
                password      TEXT,
                admin_status  INTEGER,
                result_easy   INTEGER,
                result_medium INTEGER,
                result_insame INTEGER
            )
        ''')
        if not cur.execute(f"""SELECT userid FROM users
                                             WHERE userid = 0""").fetchall():  # Проверка базы данных на наличие данных
            cur.execute(f'''INSERT INTO Users('userid', 'login', 'password', 'admin_status', 'result_easy',\
            'result_medium', 'result_insame')
                                   VALUES(0, 'admin', 'admin', 1, 0, 0, 0)''')  # Если требуется, то добовляется главный администратор
            con.commit()

        con = sqlite3.connect('db_files/levels.db')  # Создание базы данных
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                name      TEXT PRIMARY KEY,
                color_off TEXT,
                color_on  TEXT
            )
        ''')
        if not cur.execute(f"""SELECT name FROM levels
                                             WHERE name = 'Red'""").fetchall():  # Проверка базы данных на наличие данных
            for i in (('Red', '#690e00', '#ff2200'), ('Blue', '#001463', '#0033ff'), ('Yellow', '#706900', '#ffee00'),
                      ('Green', '#065202', '#0cc902'), ('Orange', '#a34e03', '#ff7800'), ('Purple', '#4b0354', '#e300ff')):
                cur = cur.execute(f'''INSERT INTO levels('name', 'color_off', 'color_on')
                                             VALUES('{i[0]}', '{i[1]}', '{i[2]}')''')  # Если требуется, то добовляются цвета секторов
            con.commit()

    def reg(self):
        """ Функция для создания окна регистрации в приложении """
        for i in self.children():  # убирание всех объектов предыдущего окна если такие найдутся
            i.setParent(None)

        self.setWindowTitle('Registration')
        self.aut = QPushButton(self)  # кнопка проверки авторизации или создания аккаунта
        self.aut.setText('Авторизация')
        self.aut.move(300, 200)
        self.aut.resize(len(self.aut.text()) * 20, 60)  # размер в зависимости от текста
        self.aut.show()

        self.login_tx = QLabel(self)  # текст запроса имени аккаунта
        self.login_tx.setText('Введите своё имя')
        self.login_tx.move(75, 150)
        self.login_tx.resize(300, 30)

        self.login = QLineEdit(self)  # запрос имени аккаунта
        self.login.setText('')
        self.login.move(75, 200)
        self.login.resize(100, 30)
        self.login.setStyleSheet('border: 1px solid black;')

        self.password_tx = QLabel(self)  # текст запроса пароля аккаунта
        self.password_tx.setText('Введите свой пароль')
        self.password_tx.move(75, 250)
        self.password_tx.resize(230, 30)

        self.password = QLineEdit(self)  # текст запроса пароля аккаунта
        self.password.setText('')
        self.password.move(75, 300)
        self.password.resize(100, 30)
        self.password.setStyleSheet('border: 1px solid black;')

        self.error = QLabel(self)  # ошибка введённых данных
        self.error.move(0, 400)
        self.error.resize(600, 30)

        for i in self.children():
            i.setFont(QFont('Times', 12))  # изменение шрифта

        self.aut.clicked.connect(self.check_aut)  # проверка введённых данных и авторизация

        for i in self.children():
            i.show()

    def check_aut(self):
        """ Функция проверки введенных данных """
        if self.password.text() and self.login.text():  # Проверка на занятость полей
            con = sqlite3.connect('db_files/gamers.db')  # Получение данных из таблицы
            cur = con.cursor()
            res = cur.execute(f"""SELECT admin_status, userid FROM users
                                                              WHERE password = '{self.password.text()}'
                                                              AND login = '{self.login.text()}'""").fetchall()  # поиск аккаунта
            if not res:  # Обработка результата
                self.error.setText('Неверно введен логин или пароль')
                return False

            self.admin, self.id = res[0]
            self.mode_tx = 'Easy'  # Выбор сложности игры по умолчанию
            self.UI()  # переход в меню
        elif not self.password.text():
            self.error.setText('Введите пароль')
        elif not self.login.text():
            self.error.setText('Введите имя пользователя')
        else:
            self.error.setText('Обратитесь к создателю и покажите как вы добились жизни такой')

    def UI(self):
        """ Функция создания основного меню игры """
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.setWindowTitle('Menu')

        self.login = QLabel(self)
        self.login.setPixmap(QPixmap('static/name.jpg'))  # картинка с названием игры
        self.login.resize(380, 140)
        self.login.move(100, 50)

        self.logout = QPushButton(self)  # кнопка перехода в правила игры
        self.logout.move(549, 0)
        self.logout.resize(51, 51)

        self.logout.clicked.connect(lambda x: self.reg())  # переход в правила игры
        icon = QIcon()
        icon.addPixmap(QPixmap("static/exit.jpg"))
        self.logout.setIcon(icon)
        self.logout.setIconSize(QSize(100, 100))

        if self.admin:
            self.rule = QPushButton('Редактирование пользователей', self)  # кнопка перехода в правила игры
            self.rule.move(100, 200)
            self.rule.resize(400, 60)
            self.rule.clicked.connect(self.admin_panel)  # переход в правила игры
            self.rule.setFont(QFont('Times', 20))
        else:
            self.rule = QPushButton('Правила игры', self)  # кнопка перехода в правила игры
            self.rule.move(100, 200)
            self.rule.resize(400, 60)
            self.rule.clicked.connect(self.rules)  # переход в правила игры
            self.rule.setFont(QFont('Times', 25))

            self.begin_game = QPushButton('Начать игру', self)  # кнопка начала игры
            self.begin_game.move(100, 400)
            self.begin_game.resize(400, 60)
            self.begin_game.clicked.connect(self.make_game)  # начало игры
            self.begin_game.setFont(QFont('Times', 25))

        self.stat = QPushButton('Рейтинг', self)  # кнопка перехода в рейтинг
        self.stat.move(100, 300)
        self.stat.resize(400, 60)
        self.stat.clicked.connect(self.table)  # переход в рейтинг
        self.stat.setFont(QFont('Times', 25))

        for i in self.children():
            i.show()

    def rules(self):
        """ Функция создания окна с правилами и выбором уровня сложности игры """
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.setWindowTitle('Rules')
        self.label = QLabel(self)
        self.label.setText('Перед вами будет круг состоящий из нескольких цветов (от 2 до 6)\nв зависимости \
от уровня сложности. С каждой правильно повторённой\nпоследовательнсотьюна нем будут загораться новый \
сектор, в свою\nочередь вам надо повторить всю последовательност\n\n\
Ваша задача, запомнить последовательность свечения секторов\nи воспроизвести её путём \
нажатия на теже сектора')
        self.label.move(0, 20)
        self.label.resize(600, 150)
        self.label.setFont(QFont('Times', 13))

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(400, 300)
        self.btn_menu.resize(200, 40)
        self.btn_menu.setFont(QFont('Times', 20))

        self.mode = QComboBox(self)  # поле выбора режима
        self.mode.move(0, 300)
        self.mode.addItem(self.mode_tx)
        for i in [j for j in ['Easy', 'Medium', 'Hard'] if j != self.mode_tx]:
            self.mode.addItem(i)
        self.mode.setFont(QFont('Times', 15))
        self.mode.resize(150, 40)

        for i in self.children():
            i.show()

        self.mode.activated.connect(self.change_mode)  # смена режима

        self.btn_menu.clicked.connect(self.UI)  # возвращение в меню

    def change_mode(self):
        """ Функция для смены режима игры """
        self.mode_tx = self.mode.currentText()  # смена режима игры

    def make_game(self):
        """ Функция для создания новой игры """
        global game

        self.close()  # скрытие меню
        game = Game()  # создание игры
        game.show()

    def paint_table(self, raiting=False):
        """ Функция отрисовки таблицы с пользовтелями """
        con = sqlite3.connect('db_files/gamers.db')
        cur = con.cursor()

        if raiting:  # Получение данных о пользователях и их обработка
            stat = list(cur.execute("""SELECT userid, login, result_easy, result_medium, result_insame FROM users
                                       WHERE admin_status = 0""").fetchall())
            self.titles = [item[0] for item in cur.description[1:5]]
            column_count = 4
            titles = ['Name', 'Easy', 'Medium', 'Hard']  # Создание заголовков для таблицы
        else:
            stat = list(cur.execute("""SELECT * FROM users""").fetchall())
            self.titles = [i[0] for i in cur.description]
            column_count = 6
            titles = ['Name', 'Password', 'Admin', 'Easy', 'Medium', 'Hard']  # Создание заголовков для таблицы

        self.statis_table = QTableWidget(len(stat), column_count, self)  # таблица рейтинга
        self.statis_table.move(0, 100)
        for i in range(column_count):
            if i != 2 and not raiting:
                self.statis_table.setColumnWidth(i, 100)  # ширина колонок
            else:
                self.statis_table.setColumnWidth(i, 70)
            self.statis_table.setHorizontalHeaderItem(i, QTableWidgetItem(titles[i]))  # название колонок

        if stat:  # Задавание размеров таблицы
            if (len(stat) + 1) * 30 < 300:
                if raiting:
                    self.statis_table.resize(305, (len(stat) + 1) * 30)
                else:
                    self.statis_table.resize(595, (len(stat) + 1) * 30)
            else:
                self.statis_table.resize(300 + (len(stat[0]) + 1) * 30, 300)
        else:
            self.statis_table.resize(300, 80)

        if raiting:
            self.statis_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # отмена возможности изменить таблицу
        else:
            stat = [i for i in sorted(stat, key=lambda x: (-x[3], x[1]))]   # Сортировка данных для таблицы
            self.all_items = [list(stat[i]) for i in range(len(stat))]
            self.statis_table.itemChanged.connect(self.item_changed)

        for i in range(len(stat)):
            for x in range(column_count):
                self.statis_table.setItem(i, x, QTableWidgetItem(str(stat[i][x + 1])))  # запись данных в таблицу

        con.close()

    def item_changed(self, item):
        """ Функция для изменения элементов в списке всех элементов """
        self.flag_of_change_item = True
        self.all_items[item.row()][item.column() + 1] = item.text()

    def admin_panel(self):
        """ Функция создания окна для адмигистрирования """
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.setWindowTitle('Admin panel')

        self.btn_remove = QPushButton('Remove', self)  # кнопка возвращения в меню
        self.btn_remove.move(0, 440)
        self.btn_remove.resize(200, 60)
        self.btn_remove.clicked.connect(self.remove_people)

        self.btn_add = QPushButton('Add', self)  # кнопка возвращения в меню
        self.btn_add.move(200, 440)
        self.btn_add.resize(200, 60)
        self.btn_add.clicked.connect(self.add_people)

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(400, 440)
        self.btn_menu.resize(200, 60)
        self.btn_menu.clicked.connect(self.check_out)

        self.rating = QLabel('Редактирование пользователей', self)  # название окна
        self.rating.move(50, 30)
        self.rating.resize(500, 60)
        self.rating.setFont(QFont('Times', 25))

        self.paint_table()

        self.flag_of_change_item = False   # Флажок значущий об отсутсвии изменений в таблице
        for i in self.children():   # Раскрытие нужных элементов на окне и изменение шрифтов
            if i != self.rating:
                i.setFont(QFont('Times', 15))
            i.show()

    def remove_people(self):
        '''Функция удаления пользователя'''
        id_acc, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter id of account:')
        if ok:
            if id_acc.isdigit() and 0 < int(id_acc) <= len(self.all_items):
                con = sqlite3.connect('db_files/gamers.db')
                cur = con.cursor()
                id_acc_cor = self.all_items[int(id_acc) - 1][0]
                if id_acc_cor == 0:
                    error = QMessageBox()
                    error.setWindowTitle("ОШИБКА")
                    error.setText("Вы не можете изменить статус главного админа!")
                    error.setIcon(QMessageBox.Icon.Warning)
                    error.setStandardButtons(
                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                    )
                    error.exec()
                else:
                    cur.execute(f'''DELETE FROM Users WHERE userid = {id_acc_cor}''')
                    con.commit()
                    self.admin_panel()
                    sucsess = QMessageBox()
                    sucsess.setWindowTitle("Успешно")
                    sucsess.setText(f"Вы удалили пользователя с id = {id_acc}")
                    sucsess.setIcon(QMessageBox.Icon.Information)
                    sucsess.setStandardButtons(
                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                    )
                    sucsess.exec()
            else:
                error = QMessageBox()
                error.setWindowTitle("ОШИБКА")
                error.setText("Такого аккаунта не существует или данные введены некорректно")
                error.setIcon(QMessageBox.Icon.Warning)
                error.setStandardButtons(
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                )
                error.exec()

    def add_people(self):
        '''Функция добавления пользователя'''
        name, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter name of account:')
        if ok:
            password, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter password of account:')
            if ok:
                con = sqlite3.connect('db_files/gamers.db')
                cur = con.cursor()
                res = cur.execute(f"""SELECT * FROM users
                                               WHERE password = '{password}'
                                               AND login = '{name}'""").fetchall()  # поиск аккаунта
                if not res:  # Обработка результата
                    id_acc = [i[0] for i in self.all_items]
                    cur.execute(f'''INSERT INTO Users('userid', 'login', 'password', 'admin_status', 'result_easy', 'result_medium', 'result_insame')
                                    VALUES({max(id_acc) + 1}, '{name}', '{password}', 0, 0, 0, 0)''')
                    con.commit()
                    self.admin_panel()
                    sucsess = QMessageBox()
                    sucsess.setWindowTitle("Успешно")
                    sucsess.setText("Вы создали нового пользователя")
                    sucsess.setIcon(QMessageBox.Icon.Information)
                    sucsess.setStandardButtons(
                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                    )
                    sucsess.exec()
                else:
                    error = QMessageBox()
                    error.setWindowTitle("ОШИБКА")
                    error.setText("Такой аккаунт уже существует или данные введены некорректно")
                    error.setIcon(QMessageBox.Icon.Warning)
                    error.setStandardButtons(
                        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                    )
                    error.exec()

    def check_out(self):
        """ Функция подтверждения изменений данных """
        if self.flag_of_change_item:
            answer = QMessageBox.question(self, '', "Вы подтверждаете изменения",
                                          buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.save_results()
        self.UI()

    def save_results(self):
        """ Сохранение данных из таблицы в db """
        for all_items in self.all_items:
            all_items = [all_items[i] for i in (0, 1, 2, 3, 4, 5, 6)]
            if all_items[0] == 0 and all_items[3] != '1':
                all_items[3] = 1
                error = QMessageBox()
                error.setWindowTitle("ОШИБКА")
                error.setText("Вы не можете изменить статус главного админа!")
                error.setIcon(QMessageBox.Icon.Warning)
                error.setStandardButtons(
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                )
                error.exec()
            con = sqlite3.connect('db_files/gamers.db')
            cur = con.cursor()
            que = "UPDATE Users SET\n"
            for i in range(7):
                que += f"{self.titles[i]} = '{all_items[i]}'"
                if i < 6:
                    que += ', '
            que += f" WHERE userid = {all_items[0]}"
            cur.execute(que)
            con.commit()
        self.all_items.clear()

    def table(self):
        """ Функция создания окна рейтинга """
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.setWindowTitle('Reting')
        self.rating = QLabel('Рейтинг', self)  # название окна
        self.rating.move(220, 30)
        self.rating.resize(200, 60)
        self.rating.setFont(QFont('Times', 25))

        self.paint_table(True)

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(440, 400)
        self.btn_menu.resize(160, 60)
        self.btn_menu.clicked.connect(self.UI)

        if self.admin:
            self.btn_save = QPushButton(self)  # кнопка сохранения таблицы
            self.btn_save.setText('Сохранить')
            self.btn_save.move(240, 400)
            self.btn_save.resize(160, 60)
            self.btn_save.clicked.connect(self.save)

        for i in self.children():  # Раскрытие нужных элементов на окне и изменение шрифтов
            if i != self.rating:
                i.setFont(QFont('Times', 15))
            i.show()

    def save(self):
        """ Функция сохранение данных о пользователях """
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter name of file:')
        if ok:
            with open(f'{text}.csv', 'w', encoding="utf8") as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"')
                writer.writerow(['name', 'result_easy', 'result_medium', 'result_insame'])

                for i in range(self.statis_table.rowCount()):
                    row = []
                    for j in range(self.statis_table.columnCount()):
                        row.append(self.statis_table.item(i, j).text())
                    writer.writerow(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = None
    menu = Menu()  # создание меню
    menu.show()  # показ меню
    sys.exit(app.exec())
