import os


# basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wait-go-ahead'
    MYSQL_DATABASE_USER = "root"
    MYSQL_DATABASE_PASSWORD = ""
    MYSQL_DATABASE_DB = "fake_news"
    MYSQL_DATABASE_HOST = "localhost"
