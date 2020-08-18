import simpy
from random import Random
import time

class Link:

    def __init__(self, env, neigh, resource):
        self._env = env
        self._neigh = neigh
        self._res = resource

    def transmit(self, msg, delay):
        request = self._res.request()
        yield self._env.timeout(delay) & request
        self._neigh.msg_queue.put(msg)
        self._res.release(request)


    def add_transmission(self, msg, delay):
        self._env.process(self.transmit(msg, delay))

class Node:
    MESSAGE_IDENTIFIER = 0

    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.link = None
        self.msg_queue = simpy.Store(env)

        self.g = Random(time.time() * hash(id))
        self.delay = Random(time.time() * hash(id + id + id))
        # self.proc = self.env.process(self.run(1))
        self.reception = self.env.process(self.recept())

    def _print(self, msg):
        print("{}-{} ".format(self.env.now, self.id) + msg)

    def add_msg_before_exec(self):
       msg = "msg: " + str(Node.MESSAGE_IDENTIFIER)
       Node.MESSAGE_IDENTIFIER += 1
       self.msg_queue.put(msg) 

    def run(self, rate):
        while True:
            yield self.env.timeout(self.g.expovariate(rate))
            msg = "msg: " + str(Node.MESSAGE_IDENTIFIER)
            Node.MESSAGE_IDENTIFIER += 1
            self._print("Sending: " + msg)
            delay = self.delay.expovariate(rate)
            self._print("delay: {} arrival time: {}".format(delay, self.env.now+delay))
            self.link.add_transmission(msg, delay)

    def recept(self):
        while True:
            self._print("Waiting an event")
            msg = yield self.msg_queue.get()
            self._print("Analized: " + msg)
            del msg

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
node1 = Node(env, 1)
node2 = Node(env, 2)
link1 = Link(env, node2, res)
link2 = Link(env, node1, res)
node1.link = link1
node2.link = link2
node1.add_msg_before_exec()
node1.add_msg_before_exec()
env.run(until=60)
