import sqlite3
import sys
import io
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


f = 'coffee.sqlite'
con = sqlite3.connect(f)
cur = con.cursor()


class AddWidget(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.pushButton.clicked.connect(self.add)
        self.id = cur.execute("SELECT * FROM cof").fetchall()

    def add(self):
        cur.execute(f'''INSERT INTO cof(id, sort, objarka, molotiy, vkus, tsena, obem)
        VALUES ('{self.id[-1][0] + 1}', '{self.lineEdit.text()}', '{self.lineEdit_2.text()}', 
        '{self.comboBox.currentText()}', '{self.lineEdit_3.text()}', '{self.lineEdit_4.text()}',
        '{self.lineEdit_5.text()}' )''')
        con.commit()
        self.parent().update_result()
        self.close()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.s = cur.execute('PRAGMA table_info("cof")')
        self.column_names = [i[1] for i in cur.fetchall()]
        self.result = cur.execute(f'''select * from cof''').fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(self.column_names)
        self.con = sqlite3.connect(f)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.pushButton.clicked.connect(self.adding)
        self.pushButton_2.clicked.connect(self.save_results)
        self.modified = {}
        self.titles = None
        self.spinBox.textChanged.connect(self.update_result)

    def adding(self):
        self.add_form = AddWidget(self)
        self.add_form.show()

    def update_result(self):
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM cof WHERE id=?",
                             (item_id := self.spinBox.text(),)).fetchall()
        if not result:
            return
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(1)
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            cur = self.con.cursor()
            que = "UPDATE cof SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += "WHERE id = ?"
            print(que)
            cur.execute(que, (self.spinBox.text(),))
            self.con.commit()
            self.modified.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
