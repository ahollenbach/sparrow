from __future__ import print_function

import socket
from Worker import Worker
import Pyro4
try:
    import queue  # py3
except ImportError:
    import Queue as queue  # py2

from Pyro4.util import SerializerBase
from Job import Job
SerializerBase.register_dict_to_class("Job.Job", Job.from_dict)

class Scheduler(object):
    METHOD_RAND = "RANDOM"
    METHOD_TWO = "CHOOSE_TWO"
    METHOD_BATCH = "BATCH"
    METHOD_LATE = "BATCH+LATE_BINDING"

    def __init__(self, scheduling_method=METHOD_RAND, nameserver_hostname="newyork"):
        self.scheduling_method = scheduling_method
        print("Scheduling method: ", self.scheduling_method)

        # List of jobs that have been scheduled/reserved
        self.in_progress_jobs = {}
        self.workers = []

        self.name_server = Pyro4.locateNS(nameserver_hostname)

    def update_workers(self):
        """ Can get very inefficient, fix """
        worker_dict = self.name_server.list('sparrow.worker')
        self.workers = []
        for key in worker_dict:
            self.workers.append(Pyro4.Proxy(worker_dict[key]))
        print(self.workers)
        # TODO doesn't handle node failure

    def schedule(self, job):
        """
        Schedules a job, which has been broken down into tasks
        :param job: A Job object
        """
        print("Scheduling job")
        self.update_workers()

        self.in_progress_jobs[job.id] = job

        for task_id in job.tasks:
            self.workers[0].add_task(job.id, task_id, job.tasks[task_id])

    def request_task(self, job_id, task_id):
        # Start with random, not needed for that
        # Will be for late binding, asking permission to start task
        raise NotImplementedError()

    def task_completed(self, job_id, task_id):
        if job_id not in self.in_progress_jobs:
            print("Job not found", job_id)
            return
        if task_id not in self.in_progress_jobs[job_id].tasks:
            print("Task not found in ", self.in_progress_jobs[job_id])
            return

        print(job_id, task_id)
        self.in_progress_jobs[job_id].tasks.pop(task_id)

        if len(self.in_progress_jobs[job_id].tasks) == 0:
            print("Job %d completed" % (self.in_progress_jobs[job_id].id))
            self.in_progress_jobs.pop(job_id)


if __name__ == "__main__":
    hostname = socket.gethostname()
    Pyro4.Daemon.serveSimple(
        {
            Scheduler(nameserver_hostname="arkansas"): "sparrow.scheduler"
        },
        host = hostname
    )
