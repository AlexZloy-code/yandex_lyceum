import random
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QInputDialog
from PyQt6.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
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

        for i in self.children():
            if i != self.timer:
                i.show()  # отрисовка всего что надо

    def end(self):
        global menu

        for i in self.children():
            i.deleteLater()  # скрытие всех элементов игры

        lib = sqlite3.connect('gamers.db')
        cur = lib.cursor()
        cur.execute(
            f"""UPDATE users SET result = '{int(menu.res.split('/')[0]) + self.nom}/{int(menu.res.split('/')[1]) + self.len}'
             WHERE login = '{menu.login}'""").fetchall()  # запись результата
        lib.commit()

        btn_menu = QPushButton('Menu', self)  # выход в меню
        btn_menu.move(400, 200)
        btn_menu.resize(200, 60)
        btn_menu.setFont(QFont('Times', 25))
        btn_menu.show()

        btn_new_game = QPushButton('Again', self)  # ещё игра
        btn_new_game.move(400, 300)
        btn_new_game.resize(200, 60)
        btn_new_game.setFont(QFont('Times', 25))
        btn_new_game.show()

        if self.nom == len(self.picture):
            win = QLabel(self)  # текст счёта
            win.move(0, 50)
            win.resize(450, 60)
            win.setFont(QFont('Times', 30))
            win.setText('Всё верно. Счёт ' + str(self.nom))
            win.show()

            congratulation = QLabel(self)  # поздравление
            congratulation.move(0, 150)
            congratulation.resize(400, 400)
            congratulation.setPixmap(QPixmap('fing.jpg'))
            congratulation.show()
        else:
            defeat = QLabel(self)  # текст счёта
            defeat.move(0, 0)
            defeat.resize(600, 60)
            defeat.setFont(QFont('Times', 25))
            defeat.setText(f'Вы ошиблись. Счёт {self.nom}')
            defeat.show()

            right = QLabel(self)  # какая ошибка
            right.move(0, 100)
            right.resize(600, 60)
            right.setFont(QFont('Times', 25))
            for i in range(self.len):
                if self.sender() == self.keys[i][1]:
                    right.setText('Правильно: ' + self.pic_login[self.keys[self.nom][2]])
                    break
                else:
                    right.setText('Другая кнопка')

            right.show()  # отображение ошибки

            btn_new_game.move(0, 200)  # размещение кнопок при допущении ошибки

            btn_menu.move(400, 200)

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

    def reg(self):
        for i in self.children():
            if i != self.bg:
                i.setParent(None)

        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap('фон.webp'))  # задавание фона авторизации и всех вкладок меню
        self.bg.resize(600, 600)  # размер фона

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
            lib = sqlite3.connect('gamers.db')
            cur = lib.cursor()
            res = cur.execute(f"""SELECT admin_status, userid FROM users
        WHERE password = '{self.password.text()}' AND login = '{self.login.text()}'""").fetchall()  # поиск аккаунта
            if not res:
                self.error.setText('Неверно введен логин или пароль')
                return False
            
            self.admin = res[0][0]
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
            if i != self.bg:
                i.setParent(None)  # скрытие элементов предыдущей вкладки

        self.setWindowTitle('Menu')
        
        self.login = QLabel(self)
        self.login.setPixmap(QPixmap('name.jpg'))  # картинка с названием игры
        self.login.resize(380, 140)
        self.login.move(100, 50)
        
        self.logout = QPushButton(self)  # кнопка перехода в правила игры
        self.logout.move(549, 0)
        self.logout.resize(51, 51)
        
        self.logout.clicked.connect(lambda x: self.reg())  # переход в правила игры
        icon = QIcon()
        icon.addPixmap(QPixmap("exit.jpg"))
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
            if i != self.bg:
                i.setParent(None)  # скрытие элементов предыдущей вкладки

        # объяснение правил
        self.label = QLabel(self)
        self.label.setText('Перед вами будет круг состоящий из нескольких цветов (от 2 до 6) в зависимости \
от\nуровня сложности поочерёдно на нем будут загораться сектора.')
        self.label.move(0, 0)
        self.label.resize(600, 120)
        self.label.setFont(QFont('Times', 11))
        self.label.show()

        self.task = QLabel(self)
        self.task.setText('Ваша задача, запомнить последовательность свечения секторов\nи воспроизвести её путём \
нажатия не теже сектора')
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
        con = sqlite3.connect('gamers.db')
        cur = con.cursor()
        
        if raiting:
            stat = list(cur.execute(f"""SELECT userid, login, result_easy, result_medium, result_insame FROM users
                                        WHERE admin_status = 0""").fetchall())  # все результаты - имена
        else:
            stat = list(cur.execute(f"""SELECT userid, login, result_easy, result_medium, result_insame, admin_status FROM users""").fetchall())
        self.titles = [item[0] for item in cur.description[1:5]]

        self.statis_table = QTableWidget(len(stat), 4, self)  # таблица рейтинга
        self.statis_table.move(0, 100)
        self.statis_table.setColumnWidth(0, 100)  # ширина 1 колонки
        self.statis_table.setColumnWidth(1, 99)  # ширина 2 колонки
        self.statis_table.setColumnWidth(2, 99)  # ширина 3 колонки
        self.statis_table.setColumnWidth(3, 99)  # ширина 4 колонки


        if stat:
            self.statis_table.resize(300 + len(stat) * 60, int((len(stat) + 1) * 30))  # размеры таблицы
        else:
            self.statis_table.resize(300 + len(stat) * 60, 80)

        self.statis_table.setHorizontalHeaderItem(0, QTableWidgetItem('Name'))  # название 1 столбца
        self.statis_table.setHorizontalHeaderItem(1, QTableWidgetItem('Easy'))  # название 2 столбца
        self.statis_table.setHorizontalHeaderItem(2, QTableWidgetItem('Medium'))  # название 3 столбца
        self.statis_table.setHorizontalHeaderItem(3, QTableWidgetItem('Hard'))  # название 4 столбца
        if raiting:
            self.statis_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # отмена возможности изменить таблицу
        else:
            stat = [i for i in sorted(stat, key=lambda x: (-x[-1], x[1]))]
            self.all_items = [[stat[i][x] for x in range(5)] for i in range(len(stat))]
            stat = [i[:5] for i in stat]
            self.statis_table.itemChanged.connect(self.item_changed)

        for i in range(len(stat)):
            for x in range(4):
                self.statis_table.setItem(i, x, QTableWidgetItem(str(stat[i][x + 1])))  # запись данных в таблицу

        con.close()

    def item_changed(self, item):
        self.flag_of_change_item = True
        self.all_items[item.row()][item.column() + 1] = item.text()

    def admin_panel(self):
        for i in self.children():
            if i != self.bg:
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
            print(all_items)
            con = sqlite3.connect('gamers.db')
            cur = con.cursor()
            que = "UPDATE Users SET\n"
            for i in range(1, 5):
                que += f"{self.titles[i - 1]} = '{all_items[i]}'"
                if i < 4:
                    que += ', '
            que += f"WHERE userid = {all_items[0]}"
            print(que)
            cur.execute(que)
            con.commit()
        self.all_items.clear()

    def table(self):
        for i in self.children():
            if i != self.bg:
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