from __future__ import print_function

import random
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

    def __init__(self, scheduling_method=METHOD_RAND, nameserver_hostname="newyork", scheduler_number=1):
        self.no_of_workers_per_scheduler = 4
        self.list_of_workers = ["newyork", "newyork", "newyork", "newyork"]
        self.list_of_schedulers = ["newyork"]
        self.scheduling_method = scheduling_method
        print("Scheduling method: ", self.scheduling_method)

        # Number of the scheduler
        self.scheduler_number = scheduler_number

        # List of jobs that have been scheduled/reserved
        self.in_progress_jobs = {}
        self.workers = []

        self.name_server = Pyro4.locateNS(nameserver_hostname)

    def update_workers(self):
        # TODO can get very inefficient
        # TODO doesn't handle node failure

        # List all sparrow workers (i.e. sparrow.worker.arizona)
        worker_dict = self.name_server.list('sparrow.worker')
        self.workers = []
        for key in worker_dict:
            self.workers.append(Pyro4.Proxy(worker_dict[key]))

        print("Workers", self.workers)

    def schedule(self, job):
        """
        Schedules a job, which has been broken down into tasks
        :param job: A Job object
        """
        print("Scheduling job")
        self.update_workers()

        self.in_progress_jobs[job.id] = job

        self.method_chosen(job)

        #for task_id in job.tasks:
        #    self.workers[0].add_task(job.id, task_id, job.tasks[task_id])

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

        print("Worker completed (job,task) ", job_id, task_id)
        self.in_progress_jobs[job_id].tasks.pop(task_id)

        if len(self.in_progress_jobs[job_id].tasks) == 0:
            print("Job %d completed" % (self.in_progress_jobs[job_id].id))
            self.in_progress_jobs.pop(job_id)

    # This method defines which method is being used to assign jobs
    def method_chosen(self, job):

        print("Choosing method of operations")

        if self.scheduling_method == "RANDOM":
            self.rand(job)
        elif self.scheduling_method == "CHOOSE_TWO":
            self.choose_two(job)
        elif self.scheduling_method == "BATCH":
            self.batch(job)
        elif self.scheduling_method == "BATCH+LATE_BINDING":
            self.late(job)

    # Implements random choosing of workers for tasks
    def rand(self, job):
        print("Random method")

        for task_id in job.tasks:
            sent = False
            while not sent:
                random_worker = random.randint(((self.scheduler_number -1)*self.no_of_workers_per_scheduler),
                                               ((self.scheduler_number*self.no_of_workers_per_scheduler) -1))
                try:
                    self.workers[random_worker].add_task(job.id, task_id, job.tasks[task_id])
                    sent = True
                except Exception as e:
                    pass

    # Implements choose two method of assigning tasks to workers
    def choose_two(self, job):
        print("Choose Two method")
        

    # Implements batch processing method of assigning tasks to workers
    def batch(self, job):
        print("Batch processing")

    # Implements Late Binding method of assigning tasks to workers
    def late(self, job):
        print("Late binding")


# Method to assign a worker number to each worker
def find_scheduler_number(list_of_schedulers):

    sched_num = 99

    host = socket.gethostname()

    if host in list_of_schedulers:
        sched_num = list_of_schedulers.index(host)

    return sched_num

if __name__ == "__main__":

    list_of_schedulers = ["newyork"]

    hostname = socket.gethostname()
    scheduler_number = find_scheduler_number(list_of_schedulers)
    if scheduler_number != 99:
        name_in_nameserver = "sparrow.scheduler" + str(scheduler_number + 1)
        Pyro4.Daemon.serveSimple(
            {
                Scheduler(): name_in_nameserver
            },
            host=hostname
        )

