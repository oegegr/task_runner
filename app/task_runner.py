import types
import urllib2
import json
import logging

from web_queue.models import DB
from web_queue.queue import TaskQueue
from config import Config


class BaseTask(object):
    def __init__(self, name, app, params=None, json_schema=None):
        """
        Basic element of task runner application
        :param name: name of the task, which maps to function
        :param app: task_runner application instance
        :param params:
        :param json_schema:
        """
        self._name = name
        self._params = params
        self._app = app
        self._json_schema = json_schema

    def run(self):
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params

    def delay(self, params=None):
        self._app.producer.delay(task_name=self._name, task_params=self._params)

    def __repr__(self):
        return 'Task %s' % self.name


class Producer(object):
    def __init__(self, url):
        self._logger = logging.getLogger('Producer')
        self.url = url
        self.request = urllib2.Request(url)
        self.request.add_header('Content-Type', 'application/json')

    def delay(self, task_name, task_params=None):
        """
        Send Rest request to queueing task
        :param task_name:
        :param task_params:
        :return:
        """
        data = {
            "name": task_name,
            "params": task_params,
        }
        json_data = json.dumps(data)
        self._logger.info('Add task %s to Queue ', task_name)
        response = urllib2.urlopen(self.request, data=json_data)


class TaskRunner(object):
    def __init__(self, db_uri, web_queue_url=Config.WEB_QUEUE_URL):
        """
        Main application contains all available tasks
        :param db_uri: database uri
        :param web_queue_url: url where is located web_queue service to queueing tasks via rest
        """
        self._tasks = {}
        self.db = DB(db_uri)
        self.tasks_queue = TaskQueue(db_uri)
        self.web_queue_url = web_queue_url
        self.producer = Producer(web_queue_url)

    def register_task_type(self, name, task):
        self._tasks[name] = task

    @property
    def tasks(self):
        return self._tasks


    def task(self, name, params=None):
        """
        Decorator, which marks functions as tasks for task_runner application.
        It creates task instace, than bounds function with task method run and register it in
        task_runner instance
        :param name:
        :param params:
        :return:
        """
        def func_wrapper(func):
            task = BaseTask(name=name, app=self, params=params)
            task.run = types.MethodType(func, task, BaseTask)
            self._tasks[name] = task
            return task
        return func_wrapper
