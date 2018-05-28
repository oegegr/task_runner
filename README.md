# Task Runner App
## System Requirements:
1. Linux OS (windows doesn't support multiprocessing)
2. PostgreSQL 9
3. Python 2
4. pip

## Installation instractions
1. git clone project, than cd to the project root directory
2. Create virtual environment for python:

    ```bash
    virtualenv .env
    ```
3. Install python dependencies:

    ```bash
    .env/bin/pip install -r requirements.txt
    ```
4. There is config.py file in the project root directory, with all main configuration settings:
    ```python
        SECRET_KEY = os.environ.get('SECRET_KEY') or "#$@#$safasdfsa23432"

        WEB_QUEUE_URL = 'http://localhost:5000/api/v1/task'

        POSTGRES_SERVER = '127.0.0.1:5433'
        POSTGRES_USER = 'postgres'
        POSTGRES_PASS = ''
        POSTGRES_DB = 'task_runner'
        SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URI')
                                    or 'postgres+psycopg2://{user}:{pw}@{db_server}/{db}'.format(user=POSTGRES_USER,
                                                                                         pw=POSTGRES_PASS,
                                                                                         db_server=POSTGRES_SERVER,
                                                                                         db=POSTGRES_DB))

        SQLALCHEMY_TRACK_MODIFICATIONS = False

    ```
5. Create database **task_runner** in postgreSQL server:
    ```sql
    -- DROP DATABASE task_runner;

    CREATE DATABASE task_runner
      WITH OWNER = postgres
           ENCODING = 'UTF8'
           TABLESPACE = pg_default
           LC_COLLATE = 'en_US.UTF-8'
           LC_CTYPE = 'en_US.UTF-8'
           CONNECTION LIMIT = -1;
    ```
## Starting web_queue application:
1. cd to project root directory
2. Start up web_queue flask application:

    ```bash
    .env/bin/python start_web_queue.py
    ```
3. Go to [web_queue app localhost:5000](http://localhost:5000/)
## Starting consumer application:
1. cd to project root directory
2. Start up consumer application with default values (--app tasks, --workers 2) in console:

    ```bash
    .env/bin/python start_consumer.py
    ```
3. start_consumer.py has two arguments:
    -  -A, --app path to application, by default it takes tasks.py from the root of project.
    -  -W, --workers number of workers, by default 2 workers. 
## Creating app with tasks 
1. The example of app locates in tasks.py in project root directory:

    ```python
    import time

    from app.task_runner import TaskRunner, BaseTask
    from config import Config

    app = TaskRunner(Config.SQLALCHEMY_DATABASE_URI)


    @app.task(name='m_sleep')
    def middle_sleep(self=None):
        print 'Middle sleep 30s'
        time.sleep(30)
        return 'Hello1'


    @app.task(name='l_sleep')
    def long_sleep(self=None):
        print 'Long sleep 60s'
        time.sleep(60)
        return 'Hello2'

    @app.task(name='inf_loop')
    def infinete_loop(self=None):
        while True:
            pass
         
    if __name__ == '__main__':
       app.tasks['l_sleep'].delay()

    ```
2. Run script with application:
    ```bash
    .env/bin/python tasks.py
    ```
3. The task will appeared in web_queue page. 
than worker will take it to process. 




