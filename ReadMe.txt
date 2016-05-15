Sparrow
Replicating Sparrow in Python

Virtual Environment - 
To run this project on the rit servers, a virtual environment will be needed.
Virtual Environment tool already exists on RIT servers.

To setup the virtual environment, ssh to an rit server and simply type the command, virtualenv name_of_environment. For example, virtualenv virt1
To activate the virtual environment, simply type the command, source name_of_environment/bin/activate. For example, source virt1/bin/activate
To deactivate the virtual environment, simply type the command, deactivate 

Alternatively, follow the instructions on this page - 
http://www.sitepoint.com/virtual-environments-python-made-easy/


Pyro4 Installation
This project uses Remote Method Invocation in python, which is provided by the pyro4 library.
This library has to be installed manually.

1. If you are using PyCharm, perform the following steps - 
	Go to `Settings > Project: name_of_project > Project Interpreter`
	  1. Hit the `+`
	  2. Search for `Pyro4` (not `Pyro`!)
	  3. Hit `Install Package`
	If that does not work, follow instructions here (https://pythonhosted.org/Pyro4/install.html)

2. To install Pyro4 on your RIT directory,
	a. Setup the virtual environment as listed above.
	b. Activate the virtual environment
	c. Type,
		pip install --upgrade pip (get the latest version of pip)
		pip install Pyro4 (install Pyro4)

		
Getting Started

Name Server
The name server is hardcoded to look at `newyork`. This can be overwritten with a `nameserver_hostname` parameter provided in most of the class
constructors. For example, python Scheduler.py BATCH+LATE_BINDING glados

	From `newyork` (or from wherever the name server is located), run:
	```bash
	cd project-dir
	source ./venv/bin/activate # May change depending on your venv location
	pyro4-ns -n newyork
	```

For the Scheduler and the Workers
This is as easy as ssh to an RIT server and run `python Scheduler.py` and `python Worker.py`, respectively.
Start the scheduler before the workers.
Note - Each worker will have to run on its own ssh connection. This means for each worker a different RIT server has to be used.


Executing a Routine
This is where we assign jobs and tasks to the scheduler. To simplify proceedings, we chose to have each task as simply telling
the worker to sleep for a certain duration of time.

To execute a routine, ssh to an rit server and run
python SparrowClient.py  method  no_of_jobs  no_of_tasks  duration  task_spread(optional)

where,
method is a string describing the method to be used.
	Options are -
	"RANDOM" - random method
	"CHOOSE_TWO" - choose two
	"BATCH" - for batch processing
	"BATCH+LATE_BINDING" - for bath processing with late binding
no_of_jobs   is an int describing the number of jobs to be completed
no_of_tasks  is an int describing the number of tasks per job
duration     is the amount of time (in seconds) each worker will sleep for
task_spread  is a float describing variations between each job (if no argument is provided here, then spreaad is set at 0.0 by default)

For example, python SparrowClient.py BATCH+LATE_BINDING 10 10 1


Running the visualization - 
Repo structure - 
Please replicate the following repo structure in order to produce the visualization.

src - directory containing Scheduler.py, __init__.py, Worker.py, SparrowClient.py, Job.py
web - directory containing Chart bundle min.js, bootstrap.min.css, index.html, main.js
server.py

SSH to an RIT server and type, python server.py

To view the visualization, open your web browser to the server address where server.py is running.

For example, if server.py is running on newyork.cs.rit.edu, go to the website, http://newyork.cs.rit.edu:8901/sparrow
