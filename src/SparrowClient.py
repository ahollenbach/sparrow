from __future__ import print_function

import Pyro4
from Scheduler import Scheduler
from Job import Job

class SparrowClient():
    def __init__(self, nameserver_hostname="newyork"):
	self.name_server = Pyro4.locateNS(nameserver_hostname)
        scheduler_uri = self.name_server.list('sparrow.scheduler')["sparrow.scheduler"]
        self.scheduler = Pyro4.core.Proxy(scheduler_uri)

    def shutdown(self):
        # TODO Do this cleaner?
        del self.scheduler

    def run(self):
        for i in range(5):
            self.scheduler.schedule(Job(i))

        # TODO tmp
        #for i in range(50):
        #    self.scheduler.workers[0].execute_task()


if __name__ == "__main__":
    client = SparrowClient(nameserver_hostname="arkansas")
    client.run()
    client.shutdown()
