from __future__ import print_function

import time
import Pyro4
import random
import thread
from Job import Job
import socket
from time import sleep
try:
    import queue  # py3
except ImportError:
    import Queue as queue  # py2

from Pyro4.util import SerializerBase

SerializerBase.register_dict_to_class("Job.Job", Job.from_dict)


class Worker(object):

    def __init__(self, name_in_nameserver, late_binding=False, nameserver_hostname="newyork"):
        """
        Creates a worker.
        :param late_binding: If true, use add_task_reservation, and worker will first place a reservation, and then
                             request the actual task when it is time to execute that reservation.
                             If false, use add_task and the task will be naively added to the queue.
        """
        self.name = name_in_nameserver
        self.late_binding = late_binding
        self.task_queue = queue.Queue()
        self.working = False

        ns = Pyro4.locateNS(nameserver_hostname)
        scheduler_dict = ns.list('sparrow.scheduler')
        for key in scheduler_dict:
            if str(1) in key:  # Hardcode 1 scheduler. If you want more, let's finish everything else first
                self.scheduler = Pyro4.core.Proxy(scheduler_dict[key])

        self.task_exec_thread = thread.start_new_thread(self.execute_tasks, ())

    def add_task(self, job_id, task_id, duration):
        """
        Adds a task to the worker's queue
        :param job_id:
        :param task_id:
        :param duration: If this is a task reservation, duration is 0
        """
        # print("adding Task")
        self.task_queue.put((job_id, task_id, duration))

    def execute_next_task(self):
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
        print("Executing <JobId:%d TaskId:%d Duration:%.2f>" % (job_id, task_id, duration))
        self.working = True
        sleep(duration)

        print("Executed <JobId:%d TaskId:%d Duration:%.2f>" % (job_id, task_id, duration))
        self.working = False

        # Report completion to scheduler
        self.scheduler.task_completed(job_id, task_id)

        return True

    # Ensures the worker is continuously executing jobs
    def execute_tasks(self):
        print("Executing Tasks")
        while True:
            if not self.task_queue.empty():
                self.execute_next_task()

    def find_load(self):
        # Find estimated time for all tasks (# tasks in queue)
        if self.working:
            return self.task_queue.qsize() +1
        else:
            return self.task_queue.qsize()

# The main method
if __name__ == "__main__":
    hostname = socket.gethostname()
    name_in_nameserver = "sparrow.worker." + hostname
    Pyro4.Daemon.serveSimple(
        {
            Worker(name_in_nameserver, late_binding=False): name_in_nameserver
        },
        host=hostname,
        ns=True
    )
