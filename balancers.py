from numpy.random import uniform
import time

def index_min(values):
   return min(xrange(len(values)),key=values.__getitem__)

class RequestAverager:
   def __init__(self):
      self.avg = dict()

   def getAverage(self, path):
      if path in self.avg:
         return self.avg[path][0]
      return 10

   def addRequest(self, request):
      old = [0.0, 0]
      if request.path in self.avg:
         old = self.avg[request.path]

      self.avg[request.path] = [(old[0] * old[1] + request.load) / (old[1] + 1), old[1] + 1]

class Balancer:
   def chooseProcessor(self, path):
      raise NotImplementedError()

   def addActualRequestLoad(self, request):
      pass

class RoundRobinBalancer(Balancer):
   def __init__(self, pool):
      self.pool = pool
      self.current = 0

   def chooseProcessor(self, path):
      val = self.current
      self.current = (self.current + 1) % self.pool.getNumProcessors()
      return val

class RandomBalancer(Balancer):
   def __init__(self, pool):
      self.pool = pool

   def chooseProcessor(self, path):
      return int(uniform() * self.pool.getNumProcessors())

class PredictiveBalancer(Balancer):
   def __init__(self, pool):
      self.pool = pool
      self.capacities = pool.getProcessorCapabilites()
      self.time = time.time()
      self.load = []
      for capacity in self.capacities:
         self.load.append(0)
      self.averager = RequestAverager()

   def chooseProcessor(self, path):
      cur = time.time()
      if (cur > self.time + 1):
         for ndx in xrange(self.pool.getNumProcessors()):
            self.load[ndx] = max(0.0, self.load[ndx] - (cur - self.time) * self.capacities[ndx])
         self.time = cur
      ndx = index_min(self.load)
      self.load[ndx] += self.averager.getAverage(path)
      return ndx

   def addActualRequestLoad(self, request):
      self.averager.addRequest(request)

class WeightedRandomBalancer(Balancer):
   def __init__(self, pool):
      self.pool = pool
      self.capacities = pool.getProcessorCapabilites()
      self.totalWeight = sum(self.capacities)

   def chooseProcessor(self, path):
      pos = int(uniform() * self.totalWeight)
      for ndx in xrange(self.pool.getNumProcessors()):
         if self.capacities[ndx] > pos:
            return ndx
         pos -= self.capacities[ndx]

class MinimumUtilizationBalancer(Balancer):
   def __init__(self, pool):
      self.pool = pool
      self.capacities = pool.getProcessorCapabilites()
      self.time = time.time()
      self.load = []
      for capacity in self.capacities:
         self.load.append(0)
      self.averager = RequestAverager()

   def chooseProcessor(self, path):
      cur = time.time()
      if (cur > self.time + 1):
         for ndx in xrange(self.pool.getNumProcessors()):
            self.load[ndx] = max(0.0, self.load[ndx] - (cur - self.time) * self.capacities[ndx])
         self.time = cur
      ndx = index_min([self.load[ndx] / self.capacities[ndx] for ndx in xrange(self.pool.getNumProcessors())])
      self.load[ndx] += self.averager.getAverage(path)
      return ndx

   def addActualRequestLoad(self, request):
      self.averager.addRequest(request)
