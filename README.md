# Sparrow
Replicating Sparrow in Python

## 1. Installation
1. In PyCharm, `VCS > Checkout From Version Control > GitHub`, then enter your GitHub credentials.
  1. For *Git Repository URL* select `https://github.com/ahollenbach/sparrow.git`
  2. For *Parent Directory* and *Directory Name* just choose where you want it.
3. Open this in a new window, and then you should just need to set up Pyro4


### Pyro4 Installation
Might be differnt for Windows, but here's what I did:

1. Go to `Settings > Project: sparrow > Project Interpreter`
  1. Hit the `+`
  2. Search for `Pyro4` (not `Pyro`!)
  3. Hit `Install Package`

Alternatively, you'll have to follow instructions [here](https://pythonhosted.org/Pyro4/install.html)

## 2. Getting Started

#### Name Server
The name server is hardcoded to look at `newyork`. You can overwrite this with a `nameserver_hostname` parameter provided in most of the class constructors if you want.
From `newyork`, run:
```bash
cd project-dir
source ./venv/bin/activate # May change depending on your venv location
pyro4-ns -n newyork
```

#### Scheduler, Workers
This is as easy as `python Scheduler.py` and `python Worker.py`. Start the scheduler before the workers.

#### Executing a Routine
`python SparrowClient.py`


## 3. Useful Links
### Documents
[Progress Report](https://docs.google.com/document/d/1TBit5KAJ3NspUf_hseIyiyxuA9Sm01CT6yI5KNSzIpI/edit)

[Design Diagram](https://docs.google.com/drawings/d/12q7JRJt6pI6HscYF3m-IuA76Mcdmzx_VhxJIZ2qQBoo/edit)

### Resources
[Sparrow Talk](https://www.youtube.com/watch?v=A4k0WqjUY9A)

[Pyro4 Tutorials](https://pythonhosted.org/Pyro4/tutorials.html)
