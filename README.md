打包方法：打开pycharam-Terminal 输入命令

带黑窗口运行版（测试时可以查看后台运行情况）:pyinstaller -D menu_collect.py -p url_parse.py -p foodgrab.py -p foodpanda.py

不带黑窗口用户使用版（加一个-w参数）:pyinstaller -D -w menu_collect.py -p url_parse.py -p foodgrab.py -p foodpanda.py

