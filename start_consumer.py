import os
import sys
import argparse

from app.task_runner import TaskRunner
from app.consumer import Consumer


def load_app(app_path):
    __import__(app_path)
    mod = sys.modules[app_path]
    from pprint import pprint
    pprint(mod)
    for o in mod.__dict__:
        if isinstance(mod.__dict__[o], TaskRunner):
            return mod.__dict__[o]
    else:
        raise ImportError()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start Consumer')
    parser.add_argument('-A', '--app', help='TaskRunner Application path', default='tasks')
    parser.add_argument('-W', '--workers', help="Number of workers", default='2')
    args = parser.parse_args()
    app = load_app(args.app)
    workers = int(args.workers)
    consumer = Consumer(app, workers)
    consumer.run()


