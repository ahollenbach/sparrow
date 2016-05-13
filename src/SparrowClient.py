from __future__ import print_function

import Pyro4
from Job import Job
import sys

class SparrowClient():
    def __init__(self, nameserver_hostname="newyork"):
        self.name_server = Pyro4.locateNS(nameserver_hostname)
        scheduler_uri = self.name_server.list('sparrow.scheduler')["sparrow.scheduler.1"]
        self.scheduler = Pyro4.Proxy(scheduler_uri)

    def run(self, method, num_jobs, num_tasks, task_length, task_spread):
        self.scheduler.set_method(method)

        for i in range(num_jobs):
            self.scheduler.schedule(Job(i, num_tasks=num_tasks, task_length=task_length, length_spread=task_spread))


if __name__ == "__main__":
    method = sys.argv[1]
    num_jobs = int(sys.argv[2])
    num_tasks = int(sys.argv[3])
    task_length = float(sys.argv[4])

    if len(sys.argv) > 5:
        task_spread = float(sys.argv[5])
    else:
        task_spread = 0.0

    client = SparrowClient()
    client.run(method, num_jobs, num_tasks, task_length, task_spread)
