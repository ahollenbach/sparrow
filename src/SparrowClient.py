from __future__ import print_function

import Pyro4
from Scheduler import Scheduler
from Job import Job

class SparrowClient():
    def __init__(self):
        # self.scheduler = Pyro4.core.Proxy("PYRONAME:sparrow.scheduler")
        self.scheduler = Scheduler()

    def shutdown(self):
        # TODO Do this cleaner?
        del self.scheduler

    def run(self):
        for i in range(5):
            self.scheduler.schedule(Job(i))

        # TODO tmp
        for i in range(50):
            self.scheduler.worker.execute_task()


if __name__ == "__main__":
    client = SparrowClient()
    client.run()
    client.shutdown()