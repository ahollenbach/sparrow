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
        self.no_of_workers_per_scheduler = 10
        self.scheduling_method = scheduling_method
        print("Scheduling method: ", self.scheduling_method)

        # Number of the scheduler
        self.scheduler_number = scheduler_number

        # List of jobs that have been scheduled/reserved
        self.in_progress_jobs = {}
        self.workers = []
        self.assigned_tasks = []
        self.name_server = Pyro4.locateNS(nameserver_hostname)

    def set_method(self, method):
        self.scheduling_method = method

        if method == Scheduler.METHOD_LATE:
            for worker in self.workers:
                worker.set_late_binding(True)
        else:
            for worker in self.workers:
                worker.set_late_binding(False)

    def update_workers(self):
        # List all sparrow workers (i.e. sparrow.worker.arizona)
        worker_dict = self.name_server.list('sparrow.worker')

        new_workers = []
        # Add new workers
        for key in worker_dict:
            worker = Pyro4.Proxy(worker_dict[key])
            new_workers.append(worker)
            if worker not in self.workers:
                self.workers.append(worker)

        # Clean nameserver
        missing_nodes = list(set(self.workers) - set(new_workers))
        for missing_node in missing_nodes:
            print("Trimming %s from nameserver." % (missing_node.name))
            self.name_server.remove(name=missing_node.name)
            # Remove local
            self.workers.remove(missing_node)

        # print(self.workers)

    def schedule(self, job):
        """
        Schedules a job, which has been broken down into tasks
        :param job: A Job object
        """
        # print("Scheduling job")
        self.update_workers()

        self.in_progress_jobs[job.id] = job

        self.method_chosen(job)

    # For late binding, worker asks for permission to start task
    def request_task(self, job_id, task_id):
        task_requested = [job_id, task_id]
        if task_requested in self.assigned_tasks:
            self.assigned_tasks.remove(task_requested)
            return True
        else:
            return False

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
        if self.scheduling_method == Scheduler.METHOD_RAND:
            self.set_method(Scheduler.METHOD_RAND)
            self.rand(job)
        elif self.scheduling_method == Scheduler.METHOD_TWO:
            self.set_method(Scheduler.METHOD_TWO)
            self.choose_two(job)
        elif self.scheduling_method == Scheduler.METHOD_BATCH:
            self.set_method(Scheduler.METHOD_BATCH)
            self.batch(job, False)
        elif self.scheduling_method == Scheduler.METHOD_LATE:
            self.set_method(Scheduler.METHOD_LATE)
            self.batch(job, True)

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
        for task_id in job.tasks:
            rand_work1 = random.randint(((self.scheduler_number -1)*self.no_of_workers_per_scheduler),
                                               ((self.scheduler_number*self.no_of_workers_per_scheduler) -1))
            done = False
            while not done:
                rand_work2 = random.randint(((self.scheduler_number -1)*self.no_of_workers_per_scheduler),
                                                   ((self.scheduler_number*self.no_of_workers_per_scheduler) -1))
                if rand_work1 != rand_work2:
                    done = True
            work1_load = self.workers[rand_work1].find_load()
            work2_load = self.workers[rand_work2].find_load()
            if int(work1_load) < int(work2_load):
                self.workers[rand_work1].add_task(job.id, task_id, job.tasks[task_id])
            else:
                self.workers[rand_work2].add_task(job.id, task_id, job.tasks[task_id])

    # Implements batch processing method of assigning tasks to workers
    # as well as batch processing plus late binding
    def batch(self, job, late_binding):
        if late_binding:
            print("Batch processing with late binding")
        else:
            print("Batch processing")

        choose = 2

        if len(self.workers) >= (choose * len(job.tasks)):
            print("Number of workers is adequate")
            random_workers = self.pick_random_workers(choose * len(job.tasks))

            if late_binding:
                for task_id in job.tasks:
                    if [job.id, task_id] not in self.assigned_tasks:
                        self.assigned_tasks.append([job.id, task_id])
                    for each_worker in random_workers:
                        self.workers[each_worker].add_task(job.id, task_id, job.tasks[task_id])
            else:
                worker_load = []
                for each in random_workers:
                    worker_load.append([self.workers[each].find_load(), each ])
                worker_load.sort()
                for task_id in job.tasks:
                    worker_id = worker_load[task_id]
                    self.workers[worker_id[1]].add_task(job.id, task_id, job.tasks[task_id])

        else:
            print("Number of workers not adequate")
            task_idx = 0
            while task_idx < len(job.tasks):
                num_workers = min(((len(job.tasks)-task_idx) * choose), len(self.workers))
                random_worker_indices = self.pick_random_workers(num_workers)

                if late_binding:
                    for task_id in range(len(random_worker_indices)/choose):
                        if [job.id, task_idx] not in self.assigned_tasks:
                            self.assigned_tasks.append([job.id, task_idx])
                        for each_worker_index in random_worker_indices:
                            self.workers[each_worker_index].add_task(job.id, task_idx, job.tasks[task_idx])
                    task_idx += 1
                else:
                    worker_load = []
                    for random_work_idx in random_worker_indices:
                        worker_load.append([self.workers[random_work_idx].find_load(), random_work_idx ])
                    worker_load.sort()
                    for task_id in range(len(random_worker_indices)/choose):
                        worker_id = worker_load[task_id]
                        self.workers[worker_id[1]].add_task(job.id, task_idx, job.tasks[task_idx])
                        task_idx += 1

    # Prints Random servers to to probe
    def pick_random_workers(self,no_of_workers_to_probe):

        random_servers = []
        while no_of_workers_to_probe > 0:
            rand_work1 = random.randint(0, len(self.workers)-1)
            if rand_work1 not in random_servers:
                random_servers.append(rand_work1)
                no_of_workers_to_probe -= 1
        # print(str(random_servers))
        return random_servers


if __name__ == "__main__":
    scheduler_number = 1
    hostname = socket.gethostname()
    name_in_nameserver = "sparrow.scheduler." + str(int(scheduler_number))
    Pyro4.config.SERVERTYPE = "multiplex"
    Pyro4.Daemon.serveSimple(
        {
            Scheduler(Scheduler.METHOD_RAND): name_in_nameserver
        },
        host=hostname
    )
