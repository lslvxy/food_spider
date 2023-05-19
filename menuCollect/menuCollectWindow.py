# -*- coding: utf-8 -*-
import os
import time
import pandas as pd
import multiprocessing
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pywinauto import keyboard
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 80, 51, 20))
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 135, 41, 21))
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(240, 110, 75, 24))
        self.lineEdit_2 = QLineEdit(Dialog)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(90, 140, 150, 22))
        # self.label_3 = QLabel(Dialog)
        # self.label_3.setObjectName(u"label_3")
        # self.label_3.setGeometry(QRect(40, 110, 49, 16))
        # self.lineEdit_3 = QLineEdit(Dialog)
        # self.lineEdit_3.setObjectName(u"lineEdit_3")
        # self.lineEdit_3.setGeometry(QRect(90, 110, 113, 22))
        self.comboBox = QComboBox(Dialog)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(90, 80, 111, 22))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u7f51\u9875\u7c7b\u578b", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"URL", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"\u786e\u5b9a", None))
        # self.label_3.setText(QCoreApplication.translate("Dialog", u"\u5730\u5740", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Dialog", u"grabfood", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Dialog", u"foodpanda", None))

class mywindow(QWidget,Ui_Dialog):
    kind = ""
    # location = ""
    url = ""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.loginFuc)

    def loginFuc(self):
        kind = self.comboBox.currentText()
        # location = self.lineEdit_3.text()
        url = self.lineEdit_2.text()
        if(kind == "grabfood"):
            self.FoodGrabCollect(url)
        elif(kind == "foodpanda"):
            self.FoodPandaCollect(url)



    def FoodGrabCollect(self, url):
        # 获取源码
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(20)
        # driver.find_element_by_class_name('textPlaceholder___1yEAK').click()
        # driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[4]/div/div/div[2]/div/div/div/span[2]').click()
        # keyboard.send_keys(location)
        # time.sleep(2)
        # keyboard.send_keys("{VK_RETURN}")
        j = 1000
        for i in range(20):
            js = f"var q=document.documentElement.scrollTop={j}"  # 某些网页直接滚动到最下方会导致部分图片未加载刷新，故采取一次刷新部分用时间循环到最低部。
            driver.execute_script(js)
            time.sleep(2)
            j += 1000
        pageSource = driver.page_source
        # foodgrab网页打开后有时会有加载不出报错的情况（500/403）采取进入循环判断是否取到值 若未取到值则再进一次循环 沉睡10s
        # 需要做到循环一个个按image,b
        # foodpanda
        # 分析源码
        # 注意：(上面注释的pagesource，可以直接传递至html_page，time.sleep(60)减少一些，这个是因为有些图片web没有渲染的话，是无法获取到对应链接的)
        html_page = pageSource
        soup = BeautifulSoup(html_page, 'lxml')
        # store_name = soup.title.text.split(' ')[0]
        store_name = url.split('/')[-1]
        # os.makedirs(f".\\{store_name}")
        total = {}
        # 定位大模块
        category_content = soup.select(".category___3C8lX")
        for i in category_content:
            # 格式化小模块信息然后 提取当前大模块下的小模块
            category_soup = BeautifulSoup(str(i), 'lxml')
            # 获取当前大模块标题
            category = category_soup.select(".categoryName___szaKI")[0].text
            os.makedirs(f".\\{store_name}\\{category}")
            # print(title)
            # 为total添加当前大模块的key
            total.update({category: []})
            item_content = category_soup.select(".menuItemWrapper___bQmSP")
            # 遍历小模块，开始逐个提取数据
            for j in item_content:
                item_soup = BeautifulSoup(str(j), 'lxml')
                # 下面开始提取信息
                try:
                    itemName = item_soup.select(".itemNameTitle___1sFBq")[0].text
                except:
                    itemName = "_"

                try:
                    itemImage = item_soup.select(".realImage___2TyNE")[0].get('src')
                    #     下载图片
                    r = requests.get(itemImage)
                    with open(f".\\{store_name}\\{category}\\{itemName}.jpg", 'wb') as f:
                        f.write(r.content)
                except:
                    itemImage = "_"
                try:
                    itemDescription = item_soup.select(".itemDescription___2cIzt")[0].text
                except:
                    itemDescription = "_"
                try:
                    save_price_res = item_soup.select(".discountText___1-XtS")[0].text
                except:
                    save_price_res = "_"
                try:
                    originalPrice = item_soup.select(".originPrice___202WH")[0].text
                except:
                    originalPrice = "_"
                try:
                    discountedPrice = item_soup.select(".discountedPrice___3MBVA")[0].text
                except:
                    discountedPrice = "_"
                try:
                    modifierGroup = item_soup.select(".sectionTitle___pw1R4")[0].text
                except:
                    modifierGroup = "_"
                try:
                    modifier = item_soup.select(".inputContentName___3-Jt8")[0].text
                except:
                    modifier = "_"
                # 将本次存储信息，存到total，用于excel输出
                total[category].append([itemName, itemDescription, save_price_res, originalPrice, discountedPrice, modifierGroup, modifier])
        # 将所有数据读取为列表格式，因为大标题，数量不够，所以空值填充,保证每个列表中的数据，列数统一
        total_excel = []
        for key, value in total.items():
            for j in value:
                total_excel.append([key, j[0], j[1], j[2], j[3], j[4], j[5], j[6]])


        # 格式化数据为dateframe格式
        df = pd.DataFrame(total_excel,
                          columns=["category", "itemName", "itemDescription", "save_price_res", "originalPrice",
                                   "discountedPrice", "modifierGroup", "modifier"])
        df.to_excel(f".\\{store_name}.xlsx", index=False)

    def FoodPandaCollect(self, url):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        # options.add_argument(f'user-agent={user_agent}')
        # options.add_argument("--window-size=1920,1050")
        driver.get(url)
        time.sleep(10)
        j = 1000
        for i in range(20):
            js = f"var q=document.documentElement.scrollTop={j}"  # 某些网页直接滚动到最下方会导致部分图片未加载刷新，故采取一次刷新部分用时间循环到最低部。
            driver.execute_script(js)
            time.sleep(3)
            j += 1000

        pageSource = driver.page_source
        soup = BeautifulSoup(pageSource, 'lxml')
        # store_name = soup.title.text.split(' ')[0]
        store_name = url.split('/')[-1]
        # os.makedirs(f".\\{store_name}")
        total = {}
        # 定位大模块

        category_content = soup.select(".box-flex.dish-category-section")
        # category_content = soup.select(".menu__items-wrapper")
        for i in category_content:
            # 格式化小模块信息然后 提取当前大模块下的小模块
            category_soup = BeautifulSoup(str(i), 'lxml')
            # 获取当前大模块标题
            category = category_soup.select(".dish-category-title")[0].text
            os.makedirs(f".\\{store_name}\\{category}")
            # category = category_soup.find(attrs={
            #     'class': "dish-category-title cl-neutral-primary f-title-large-font-size fw-title-large-font-weight lh-title-large-line-height"}).text
            # 为total添加当前大模块的key
            total.update({category: []})
            item_content = category_soup.select(".box-flex.dish-card")
            # item_content = category_soup.find_all(attrs={
            #     'class': "box-flex dish-card bg-white jc-space-between p-relative sm:pl-zero md:pl-md lg:pl-md pl-sm sm:pr-zero md:pr-md lg:pr-md pr-sm sm:pt-zero md:pt-md lg:pt-md pt-sm sm:pb-sm md:pb-md lg:pb-md pb-sm br-xxs bs-1"})
            # 遍历小模块，开始逐个提取数据
            for j in item_content:
                item_soup = BeautifulSoup(str(j), 'lxml')
                # 下面开始提取信息
                try:
                    #itemName = item_soup.find(attrs={'class': "vertical-align-middle"}).text
                    itemName = item_soup.select(".vertical-align-middle")[0].text
                except:
                    itemName = "_"
                try:
                    #itemImage = item_soup.find(attrs={'class': "lazy-loaded-dish-photo"}).get('style').split('"')[1].split('?')[0]
                    itemImage = item_soup.select(".lazy-loaded-dish-photo")[0].get('style').split('"')[1].split('?')[0]
                    #     下载图片
                    r = requests.get(itemImage)
                    with open(f".\\{store_name}\\{category}\\{itemName}.jpg", 'wb') as f:
                        f.write(r.content)
                except:
                    itemImage = "_"
                try:
                    # itemDescription = minimum_soup.find(attrs={
                    #     'class': "dish-description truncate cl-neutral-secondary f-paragraph-small-font-size fw-paragraph-small-font-weight lh-paragraph-small-line-height mt-xxs"}).text
                    itemDescription = item_soup.select(".dish-description")[0].text
                except:
                    itemDescription = "_"
                # try:
                #     save_pice_res = minimum_soup.find(attrs={'class': "discountText___1-XtS"}).text
                # except:
                #     save_pice_res = "xxx空"
                # try:
                #     originalPrice = minimum_soup.find(attrs={'class': "originPrice___202WH"}).text
                # except:
                #     originalPrice = "xxx空"
                try:
                    # originalPrice = item_soup.find(attrs={
                    #     'class': "cl-neutral-primary sm:f-ribbon-base-font-size f-label-large-font-size sm:fw-ribbon-base-font-weight fw-label-large-font-weight sm:lh-ribbon-base-line-height lh-label-large-line-height mr-xs mt-xxs"}).text
                    originalPrice = item_soup.select(".cl-neutral-primary")[1].text
                except:
                    originalPrice = "_"
                # try:
                #     modifierGroup = minimum_soup.find(attrs={'class': "sectionTitle___pw1R4"}).text
                # except:
                #     modifierGroup = "xxx空"
                # try:
                #     modifier = minimum_soup.find(attrs={'class': "inputContentName___3-Jt8"}).text
                # except:
                #     modifier = "xxx空"
                # 将本次存储信息，存到total，用于excel输出
                total[category].append([itemName, itemDescription, originalPrice])

        total_excel = []
        # 将所有数据读取为列表格式，因为大标题，数量不够，所以空值填充,保证每个列表中的数据，列数统一
        for key, value in total.items():
            for j in value:
                total_excel.append([key, j[0], j[1], j[2]])
        # 格式化数据为dateframe格式
        df = pd.DataFrame(total_excel, columns=["category", "itemName", "itemDescription", "originalPrice"])
        df.to_excel(f".\\{store_name}.xlsx", index=False)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication([])
    window=mywindow()
    window.show()
    app.exec()