from __future__ import print_function

import random

class Job(object):
    def __init__(self, id, num_tasks=10, task_length=0.1, length_spread=0.0):
        """
        Create the job object.

        :param num_tasks: Number of tasks in this job
        :param task_length: Length (in seconds) of each task. In a heterogeneous task, acts as the mean task length
        :param length_spread: Spread (in seconds) from the mean, for heterogeneous tasks. Random spread.
        """
        self.id = id
        self.num_tasks = num_tasks
        self.task_length = task_length
        self.length_spread = length_spread

        # A list of "tasks" (number of seconds to sleep)
        self.tasks = {}

        for i in range(num_tasks):
            self.tasks[i] = random.uniform(task_length-length_spread, task_length+length_spread)

    def __str__(self):
        return "Job %d: %d %.2f %.2f" % (self.id, self.num_tasks, self.task_length, self.length_spread)

    @staticmethod
    def from_dict(classname, d):
        assert classname == "Job.Job"
        j = Job(d["id"], d["num_tasks"], d["task_length"], d["length_spread"])
        return j

if __name__ == "__main__":
    # Test
    j = Job(0, length_spread=0.1)
    print(j)
    print(j.tasks)