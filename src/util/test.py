import simpy
from random import Random
import time


class Node:
    MESSAGE_IDENTIFIER = 0

    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.queue = []
        self.rec_ev = self.env.event()
        self.g = Random(time.time() * hash(id))
        self.proc = self.env.process(self.run(1))
        self.neigh = None
        self.reception = self.env.process(self.recept())

    def _print(self, msg):
        print("{}-{} ".format(self.env.now, self.id) + msg)

    def run(self, rate):
        while True:
            yield self.env.timeout(self.g.expovariate(rate))
            msg = "msg: " + str(Node.MESSAGE_IDENTIFIER)
            Node.MESSAGE_IDENTIFIER += 1
            self._print("Sending msg: " + msg)
            self.neigh.event_handler(msg)

    def event_handler(self, event):
        self.queue.insert(0, event)
        self._print("Message received: " + event)
        self.rec_ev.succeed()
        self.rec_ev = self.env.event()

    def recept(self):
        while True:
            if len(self.queue) > 0:
                m = self.queue.pop()
                yield self.env.timeout(1)
                self._print("Analized message: " + m)
                del m

            if len(self.queue) == 0:
                yield self.rec_ev


env = simpy.Environment()
node1 = Node(env, 1)
node2 = Node(env, 2)
node1.neigh = node2
node2.neigh = node1
env.run(until=60)
