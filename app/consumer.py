import logging
import signal
import time
import sys, traceback
from multiprocessing import Event as ProcessEvent
from multiprocessing import Process

from web_queue.queue import TaskQueue, TaskResults
from config import Config

logging.basicConfig(level=logging.INFO)


class Worker(object):
    def __init__(self, task_runner, worker_id, delay):
        """
        Worker object run tasks. If task_queue is empty, worker sleep
        :param task_runner: task_runner application with tasks
        :param worker_id: id of current worker
        :param delay: how long worker should sleep
        """
        logger = 'Consumer.%s' % worker_id
        self._logger = logging.getLogger(logger)
        self.delay = delay
        self.task_runner = task_runner
        self.task_queue = TaskQueue()
        self.task_results = TaskResults()
        self.tasks = self.task_runner.tasks
        self.worker_id = worker_id

    def loop(self):
        task = None
        exception = True
        queued_task = None
        try:
            queued_task = self.task_queue.peek(worker_id=self.worker_id)
            if queued_task:
                self._logger.info('Trying to get task from TaskRunner %s', queued_task.name)
                task = self.tasks.get(queued_task.name)
        except KeyboardInterrupt:
            raise
        except:
            self._logger.info('Unknown Error')
            traceback.print_exc(file=sys.stdout)
        else:
            exception = False
        if task:
            self.process_task(task, queued_task.id)
        else:
            self._logger.info('No messages in Task Queue, It is sleep time for %d s', self.delay)
            time.sleep(self.delay)

    def process_task(self, task, task_id):
        status = 'BAD'
        exception = True
        try:
            self._logger.info('Processing Task')
            task_result = task.run()
            self.task_queue.delete(task_id)
            exception = False
        except KeyboardInterrupt:
            self._logger.info('Receiving exit signal')
        except:
            self._logger.info('Unhandled exception in working thread')
            traceback.print_exc(file=sys.stdout)
        if exception:
            self.task_results.save_result(task.name, status)
            self._logger.info('Save bad task result')
            self.task_queue.delete(task_id)
            self._logger.info('Remove bad task from queue')
        else:
            status = 'OK'
            self.task_results.save_result(task.name, status, task_result)
            self._logger.info('Save good task result')



class Consumer(object):
    def __init__(self, app, workers=1):
        """
        Consumer creates worker process and starts them in the loop.
        :param app: task_runner instance application, with all available tasks
        :param workers: the number of worker to start
        """
        self.consumer_timeout = 0.1
        self.max_delay = 10
        self._logger = logging.getLogger('Consumer')
        self._logger.setLevel(logging.INFO)
        self.app = app
        self.workers_process = []
        for i in range(workers):
            worker_id = 'Worker-%d' % (i+1)
            worker = self._create_worker(worker_id)
            process = self._create_process(worker, worker_id)
            self.workers_process.append((worker, process))

    def _create_worker(self, worker_id):
        return Worker(self.app, worker_id, self.max_delay)

    def _create_process(self, process, name):
        def _run():
            try:
                while True:
                    process.loop()
            except KeyboardInterrupt:
                pass
            except:
                self._logger.exception('Process %s died', name)
        p = Process(target=_run, name=name)
        p.daemon = True
        return p

    def start(self):
        self._logger.info('Starting Consumer')
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        if hasattr(signal, 'SIGHUP'):
            original_sighup_handler = signal.signal(signal.SIGHUP, signal.SIG_IGN)

        for _, worker in self.workers_process:
            worker.start()

        signal.signal(signal.SIGINT, original_sigint_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, original_sighup_handler)

    def stop(self, graceful=False):
        if graceful:
            self._logger.info('Shutting down gracefully...')
            try:
                for _, worker in self.workers_process:
                    worker.join(10)
            except KeyboardInterrupt:
                self._logger.info('Request for shutting down...')
            else:
                self._logger.info('All workers have stopped')
        else:
            self._logger.info('Shutting down...')

    def run(self):
        """
        run method start up Consumer
        :return:
        """
        self.start()
        timeout = self.consumer_timeout
        self._logger.info("Consumer started")
        while True:
            try:
                time.sleep(timeout)
                # self._logger.info("Loop started")
            except KeyboardInterrupt:
                self._logger.info("Keyboard Iterrupt")
                self.stop(graceful=True)
            except:
                self._logger.info('Error in Consumer')
                self.stop()

