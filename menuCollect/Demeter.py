# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_password_request.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

import logging
from url_parse import parse
from foodgrab import parse_foodgrab
from foodpanda import parse_foodpanda
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
                               QPushButton, QSizePolicy, QWidget, QListWidget, QVBoxLayout)

class Ui_menuSelect(object):
    def setupUi(self, menuSelect):
        if not menuSelect.objectName():
            menuSelect.setObjectName(u"menuSelect")
        menuSelect.resize(474, 284)
        self.label = QLabel(menuSelect)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 80, 31, 16))
        self.pushButton = QPushButton(menuSelect)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(340, 203, 111, 31))
        self.lineEdit = QLineEdit(menuSelect)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(80, 80, 311, 22))
        self.lineEdit.setText("https://www.foodpanda.com.tw/en/restaurant/w3ki/ji-ye-jia-yoshinoya-xin-bei-yong-he-dian")

        self.retranslateUi(menuSelect)

        QMetaObject.connectSlotsByName(menuSelect)
    # setupUi

    def retranslateUi(self, menuSelect):
        menuSelect.setWindowTitle(QCoreApplication.translate("menuSelect", u"Demeter", None))
        self.label.setText(QCoreApplication.translate("menuSelect", u"URL", None))
        self.pushButton.setText(QCoreApplication.translate("menuSelect", u"confirm", None))
    # retranslateUi



class mywindow(QWidget, Ui_menuSelect):
    url = ""
    a = []
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 下面两行
        self.ListWidget=QListWidget()
        self.mainLayout = QVBoxLayout()
        self.pushButton.clicked.connect(self.loginFuc)

    def loginFuc(self):
        url = self.lineEdit.text()
        page_url = url

        variables = parse(page_url)
        if variables == {}:
            self.a = 'Unsupported page addresses'
            self.ListWidget.addItem(self.a)
            logging.info('Unsupported page addresses')
        else:
            if variables.get('type') == 'foodgrab':

                self.a = parse_foodgrab(page_url, variables)
                for i in self.a:
                    self.ListWidget.addItem(i)
                self.mainLayout.addWidget(self.ListWidget)
                self.setLayout(self.mainLayout)
                parse_foodgrab(page_url, variables)
            elif variables.get('type') == 'foodpanda':

                self.a = parse_foodpanda(page_url, variables)
                for i in self.a:
                    self.ListWidget.addItem(i)
                self.mainLayout.addWidget(self.ListWidget)
                self.setLayout(self.mainLayout)
                parse_foodpanda(page_url, variables)
            # print(variables)



if __name__ == '__main__':
    app = QApplication([])
    window = mywindow()
    window.show()
    app.exec()