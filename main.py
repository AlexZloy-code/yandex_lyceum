import random
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QInputDialog
from PyQt6.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt6.QtGui import QFont, QIcon, QMouseEvent, QPixmap, QPainter, QBrush, QColor
from PyQt6 import QtCore
import sqlite3
import csv


def make_menu(self):
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
        
        self.login = QLabel(self)
        self.login.setText(f'Уровень игры: {menu.mode_tx}')
        self.login.resize(290, 25)
        self.login.move(100, 0)
        self.login.setFont(QFont('Times', 20))
        self.cor_posled = []
        self.posled = []

        mas = ['Red', 'Green', 'Blue', 'Yellow', 'Purple', 'Orange']
        con = sqlite3.connect('db_files/levels.db')
        cur = con.cursor()
        if menu.mode_tx == 'Easy':
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
        time = QtCore.QDateTime.currentDateTime().addSecs(1)
        while QtCore.QDateTime.currentDateTime() < time:
            pass
        self.mode = True
        self.update()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if (event.pos().x() - 230) ** 2 + (event.pos().y() - 220) ** 2 <= 150 ** 2:
            if menu.mode_tx == 'Easy':
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
            self.posled.append(i)
            if self.posled != self.cor_posled[:len(self.posled)]:
                self.setMouseTracking(False)
                return self.end()
            elif self.posled == self.cor_posled:
                self.make_posled()

    def paintEvent(self, event):
        if self.do_paint:
            painter = QPainter()
            painter.begin(self)
            if self.do_paint_start:
                if menu.mode_tx == 'Easy':
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
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0], self.color5[0], self.color6[0]):
                        painter.setBrush(QBrush(QColor(color)))
                        painter.drawPie(80, 70, 300, 300, i * 16, 60 * 16)
                        i += 60
                self.do_paint_start = False
            else:
                if menu.mode_tx == 'Easy':
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
                    for color in (self.color1[0], self.color2[0], self.color3[0], self.color4[0], self.color5[0], self.color6[0]):
                        if color != color1[0]:
                            painter.setBrush(QBrush(QColor(color)))
                        else:
                            painter.setBrush(QBrush(QColor(color1[1])))
                        painter.drawPie(80, 70, 300, 300, j * 16, 60 * 16)
                        j += 60
                    if self.mode:
                        painter.setBrush(QBrush(QColor(color1[0])))
                        painter.drawPie(80, 70, 300, 300, j1 * 16, 60 * 16)
                self.proba()
            painter.end()

    def end(self):
        global menu

        con = sqlite3.connect('db_files/gamers.db')
        cur = con.cursor()
        mas1 = ['Easy', 'Medium', 'Hard']
        mas2 = ['result_easy', 'result_medium', 'result_insame']
        mode = mas2[mas1.index(menu.mode_tx)]
        schet = cur.execute(f"""SELECT {mode} FROM users
                                              WHERE userid = '{menu.id}'""").fetchall()
        cur.execute(
            f"""UPDATE users SET {mode} = '{max(schet[0][0], len(self.cor_posled) - 1)}'
                WHERE userid = '{menu.id}'""").fetchall()  # запись результата
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
        global game

        self.deleteLater()  # уничтожение прошлой игры

        game = Game()  # создание новой игры
        game.show()


class Menu(QWidget):  # класс меню
    def __init__(self):
        super().__init__()
        self.reg()
        self.setGeometry(0, 0, 600, 500)

    def reg(self):
        for i in self.children():
            i.setParent(None)

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

        self.password_tx = QLabel(self)  # текст запроса пароля аккаунта
        self.password_tx.setText('Введите свой пароль')
        self.password_tx.move(75, 250)
        self.password_tx.resize(230, 30)

        self.password = QLineEdit(self)  # текст запроса пароля аккаунта
        self.password.setText('')
        self.password.move(75, 300)
        self.password.resize(100, 30)

        self.error = QLabel(self)  # ошибка введённых данных
        self.error.move(0, 400)
        self.error.resize(600, 30)

        for i in self.children():
            i.setFont(QFont('Times', 12))  # изменение шрифта

        self.aut.clicked.connect(self.check_aut)  # проверка введённых данных и авторизация

        for i in self.children():
            i.show()

    def check_aut(self):
        if self.password.text() and self.login.text():
            con = sqlite3.connect('db_files/gamers.db')
            cur = con.cursor()
            res = cur.execute(f"""SELECT admin_status, userid FROM users
                                                              WHERE password = '{self.password.text()}' 
                                                              AND login = '{self.login.text()}'""").fetchall()  # поиск аккаунта
            if not res:
                self.error.setText('Неверно введен логин или пароль')
                return False
            
            self.admin, self.id = res[0]
            self.mode_tx = 'Easy'
            self.UI()  # переход в меню
        elif not self.password.text():
            self.error.setText('Введите пароль')
        elif not self.login.text():
            self.error.setText('Введите имя пользователя')
        else:
            self.error.setText('Обратитесь к создателю и покажите как вы добились жизни такой')

    def UI(self):
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
        self.logout.setIconSize(QtCore.QSize(100, 100))

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
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        # объяснение правил
        self.label = QLabel(self)
        self.label.setText('Перед вами будет круг состоящий из нескольких цветов (от 2 до 6) в зависимости \
от\nуровня сложности. С каждой правильно повторённой последовательнсотью на нем будут\nзагораться новый \
сектор, в свою очередь вам надо повторить всю последовательность.')
        self.label.move(0, 0)
        self.label.resize(600, 120)
        self.label.setFont(QFont('Times', 11))
        self.label.show()

        self.task = QLabel(self)
        self.task.setText('Ваша задача, запомнить последовательность свечения секторов\nи воспроизвести её путём \
нажатия на теже сектора')
        self.task.move(0, 120)
        self.task.resize(600, 120)
        self.task.setFont(QFont('Times', 13))
        self.task.show()

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(400, 300)
        self.btn_menu.resize(200, 40)
        self.btn_menu.setFont(QFont('Times', 20))
        self.btn_menu.show()

        self.mode = QComboBox(self)  # поле выбора режима
        self.mode.move(0, 300)
        self.mode.addItem(self.mode_tx)
        for i in [j for j in ['Easy', 'Medium', 'Hard'] if j != self.mode_tx]:
            self.mode.addItem(i)
        self.mode.setFont(QFont('Times', 15))
        self.mode.resize(150, 40)
        self.mode.show()

        self.mode.activated.connect(self.change_mode)  # смена режима

        self.btn_menu.clicked.connect(self.UI)  # возвращение в меню

    def change_mode(self):
        self.mode_tx = self.mode.currentText()  # смена режима

    def make_game(self):
        global game

        self.close()  # скрытие меню
        game = Game()  # создание игры
        game.show()
        
    def paint_table(self, raiting=False):
        con = sqlite3.connect('db_files/gamers.db')
        cur = con.cursor()
        
        if raiting:
            stat = list(cur.execute(f"""SELECT userid, login, result_easy, result_medium, result_insame FROM users
                                        WHERE admin_status = 0""").fetchall())  # все результаты - имена
            self.titles = [item[0] for item in cur.description[1:5]]
            column_count = 4
            titles = ['Name', 'Easy', 'Medium', 'Hard']
        else:
            stat = list(cur.execute(f"""SELECT userid, login, password, result_easy, result_medium, result_insame, admin_status FROM users""").fetchall())
            self.titles = [item[0] for item in cur.description[1:6]]
            column_count = 5
            titles = ['Name', 'Password', 'Easy', 'Medium', 'Hard']

        self.statis_table = QTableWidget(len(stat), column_count, self)  # таблица рейтинга
        self.statis_table.move(0, 100)
        for i in range(column_count):
            self.statis_table.setColumnWidth(i, 100)  # ширина колонок
            self.statis_table.setHorizontalHeaderItem(i, QTableWidgetItem(titles[i]))  # название колонок

        if stat:
            self.statis_table.resize(300 + len(stat) * 65, int((len(stat) + 1) * 30))  # размеры таблицы
        else:
            self.statis_table.resize(300 + len(stat) * 60, 80)
        
        if raiting:
            self.statis_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # отмена возможности изменить таблицу
        else:
            stat = [i for i in sorted(stat, key=lambda x: (-x[-1], x[1]))]
            self.all_items = [[stat[i][x] for x in range(6)] for i in range(len(stat))]
            stat = [i[:6] for i in stat]
            self.statis_table.itemChanged.connect(self.item_changed)

        for i in range(len(stat)):
            for x in range(column_count):
                self.statis_table.setItem(i, x, QTableWidgetItem(str(stat[i][x + 1])))  # запись данных в таблицу

        con.close()

    def item_changed(self, item):
        self.flag_of_change_item = True
        self.all_items[item.row()][item.column() + 1] = item.text()

    def admin_panel(self):
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(400, 300)
        self.btn_menu.resize(200, 60)
        self.btn_menu.clicked.connect(self.check_out)

        self.rating = QLabel('Редактирование пользователей', self)  # название окна
        self.rating.move(200, 30)
        self.rating.resize(200, 60)
        self.rating.setFont(QFont('Times', 25))

        self.flag_of_change_item = False
        self.all_items = list()

        self.paint_table()

        for i in self.children():
            if i != self.rating:
                i.setFont(QFont('Times', 15))
            i.show()

    def check_out(self):
        if self.flag_of_change_item:
            answer = QMessageBox.question(self, '', "Вы подтверждаете изменения",
                                          buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                self.save_results()
        self.UI()

    def save_results(self):
        for all_items in self.all_items:
            con = sqlite3.connect('db_files/gamers.db')
            cur = con.cursor()
            que = "UPDATE Users SET\n"
            for i in range(1, 6):
                que += f"{self.titles[i - 1]} = '{all_items[i]}'"
                if i < 5:
                    que += ', '
            que += f"WHERE userid = {all_items[0]}"
            cur.execute(que)
            con.commit()
        self.all_items.clear()

    def table(self):
        for i in self.children():
            i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.btn_menu = QPushButton('Menu', self)  # кнопка возвращения в меню
        self.btn_menu.move(400, 300)
        self.btn_menu.resize(200, 60)
        self.btn_menu.clicked.connect(self.UI)

        self.rating = QLabel('Рейтинг', self)  # название окна
        self.rating.move(200, 30)
        self.rating.resize(200, 60)
        self.rating.setFont(QFont('Times', 25))

        self.paint_table(True)

        if self.admin:
            self.btn_save = QPushButton(self)  # кнопка сохранения таблицы
            self.btn_save.setText('Сохранить')
            self.btn_save.move(200, 300)
            self.btn_save.resize(200, 60)
            self.btn_save.clicked.connect(self.save)

        for i in self.children():
            if i != self.rating:
                i.setFont(QFont('Times', 15))
            i.show()

    def save(self):
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