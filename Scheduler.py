from __future__ import print_function

from Worker import Worker
import Pyro4
try:
    import queue  # py3
except ImportError:
    import Queue as queue  # py2

class Scheduler(object):
    METHOD_RAND = "RANDOM"
    METHOD_TWO = "CHOOSE_TWO"
    METHOD_BATCH = "BATCH"
    METHOD_LATE = "BATCH+LATE_BINDING"

    def __init__(self, scheduling_method=METHOD_RAND):
        self.scheduling_method = scheduling_method
        print("Scheduling method: ", self.scheduling_method)

        # List of jobs that have been scheduled/reserved
        self.in_progress_jobs = {}

        # TODO temp, remove and distribute
        self.worker = Worker(self)

    def schedule(self, job):
        """
        Schedules a job, which has been broken down into tasks
        :param job: A Job object
        """
        self.in_progress_jobs[job.id] = job

        for task_id in job.tasks:
            self.worker.add_task(job.id, task_id, job.tasks[task_id])

    def request_task(self, job_id, task_id):
        # Start with random, not needed for that
        # Will be for late binding, asking permission to start task
        raise NotImplementedError()

    def task_completed(self, job_id, task_id):
        if task_id not in self.in_progress_jobs[job_id].tasks:
            print("Task not found in ", self.in_progress_jobs[job_id])

        self.in_progress_jobs[job_id].tasks.pop(task_id)

        if len(self.in_progress_jobs[job_id].tasks) == 0:
            print("Job %d completed" % (self.in_progress_jobs[job_id].id))
            self.in_progress_jobs.pop(job_id)


if __name__ == "__main__":
    Pyro4.Daemon.serveSimple({
        Scheduler(): "sparrow.scheduler"
    })