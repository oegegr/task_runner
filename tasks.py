import time

from app.task_runner import TaskRunner
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
    app.tasks['m_sleep'].delay()


