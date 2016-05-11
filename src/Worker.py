from __future__ import print_function

import Pyro4
import socket
from time import sleep
try:
    import queue  # py3
except ImportError:
    import Queue as queue  # py2

class Worker(object):
    def __init__(self, late_binding=False, nameserver_hostname="newyork"):  # scheduler only temporary
        """
        Creates a worker.

        :param late_binding: If true, use add_task_reservation, and worker will first place a reservation, and then
                             request the actual task when it is time to execute that reservation.
                             If false, use add_task and the task will be naively added to the queue.
        """
        self.late_binding = late_binding
        self.task_queue = queue.Queue()

        # Assume one scheduler for now
        ns = Pyro4.locateNS(nameserver_hostname)
        print(ns)
        scheduler_uri = ns.list('sparrow.scheduler')["sparrow.scheduler"]
        self.scheduler = Pyro4.core.Proxy(scheduler_uri)
        print(self.scheduler)

    def add_task(self, job_id, task_id, duration):
        """
        Adds a task to the worker's queue

        :param job_id:
        :param task_id:
        :param duration: If this is a task reservation, duration is 0
        """
        self.task_queue.put((job_id, task_id, duration))

    def execute_task(self):
        if self.task_queue.qsize() == 0:
            return False

        if self.late_binding:
            job_id, task_id, duration = self.task_queue.get()

            if not self.scheduler.request_task(job_id, task_id):
                # Task has already been completed
                return
        else:
            job_id, task_id, duration = self.task_queue.get()

        # "Execute" our task
        sleep(duration)

        # Report completion to scheduler
        self.scheduler.task_completed(job_id, task_id)

        return True

if __name__ == "__main__":
    hostname = socket.gethostname()
    Pyro4.Daemon.serveSimple(
        {
            Worker(nameserver_hostname="arkansas"): "sparrow.worker"
        },
        host = hostname
    )