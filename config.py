import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or "#$@#$safasdfsa23432"

    WEB_QUEUE_URL = 'http://localhost:5000/api/v1/task'

    POSTGRES_SERVER = '127.0.0.1:5432'
    POSTGRES_USER = 'postgres'
    POSTGRES_PASS = ''
    POSTGRES_DB = 'task_runner'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URI')
                                or 'postgres+psycopg2://{user}:{pw}@{db_server}/{db}'.format(user=POSTGRES_USER,
                                                                                     pw=POSTGRES_PASS,
                                                                                     db_server=POSTGRES_SERVER,
                                                                                     db=POSTGRES_DB))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

