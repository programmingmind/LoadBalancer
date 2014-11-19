from heapq import heappush, heappop
import threading
import time

class TimeKeeper:
   def time(self):
      raise NotImplementedError()

   def sleep(self, duration):
      raise NotImplementedError()

   def threadDone(self):
      pass

class RealTimeKeeper(TimeKeeper):
   def time(self):
      return time.time()

   def sleep(self, duration):
      time.sleep(duration)

class SimulatedTimeKeeper(TimeKeeper):
   def __init__(self, minimumToAdvance):
      self.clock = time.time()
      self.minimumToAdvance = minimumToAdvance
      self.pending = []
      self.lock = threading.Lock()

   def time(self):
      return self.clock

   def sleep(self, duration):
      until = self.time() + duration
      
      self.lock.acquire()

      heappush(self.pending, until)

      if len(self.pending) >= self.minimumToAdvance and len(self.pending) > 0:
         self.clock = heappop(self.pending)

      self.lock.release()

      while self.time() < until:
         time.sleep(0.001)

   def threadDone(self):
      self.lock.acquire()
      self.minimumToAdvance -= 1

      if len(self.pending) >= self.minimumToAdvance and len(self.pending) > 0:
         self.clock = heappop(self.pending)

      self.lock.release()