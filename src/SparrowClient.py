from __future__ import print_function

import Pyro4
from Job import Job

class SparrowClient():
    def __init__(self, nameserver_hostname="newyork"):
        self.name_server = Pyro4.locateNS(nameserver_hostname)
        scheduler_uri = self.name_server.list('sparrow.scheduler')["sparrow.scheduler.1"]
        self.scheduler = Pyro4.Proxy(scheduler_uri)

    def run(self):
        for i in range(1):
            self.scheduler.schedule(Job(i, num_tasks=5, task_length=1))


if __name__ == "__main__":
    client = SparrowClient()
    client.run()
