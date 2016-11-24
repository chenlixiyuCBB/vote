# encoding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter,getLogger

# 初始化App
app = Flask(__name__)
app.config.from_pyfile("config.py", silent=True)
db = SQLAlchemy(app)

# 初始化日志输出
hanlder = logging.FileHandler("../vote.log",encoding="utf-8")
logging_format = Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s'' - %(funcName)s - %(lineno)s - %(message)s') # 日志格式
hanlder.setFormatter(logging_format)
logs = [app.logger,getLogger("sqlalchemy")]
for log in logs:
    log.addHandler(hanlder)

import view
import model

# 初始化数据库
db.create_all()
db.session.commit()

import cache
