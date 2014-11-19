import balancers
from collections import deque
import json
from numpy.random import randn, uniform
import sys
import timers
import threading

class Processor (threading.Thread):
   def __init__(self, threadID, workCapacity, timer, period):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.workCapacity = workCapacity
      self.timer = timer
      self.lastTime = timer.time()
      self.load = 0.0
      self.lock = threading.Lock()
      self.outfile = open("Thread" + str(threadID) + ".log", 'w')
      self.running = True
      self.daemon = True
      self.period = period
      self.toWrite = []
      self.lastWrite = self.lastTime

   def getLoad(self):
      self.lock.acquire()
      load = self.load
      self.lock.release()

      return load

   def processLoad(self):
      self.lock.acquire()

      curTime = self.timer.time()
      self.load -= self.workCapacity * (curTime - self.lastTime)
      if self.load < 0:
         self.load = 0

      self.lock.release()

      self.lastTime = curTime
      return curTime

   def addLoad(self, load):
      self.lock.acquire()
      self.load += load
      self.lock.release()

   def run(self):
      while self.running or self.getLoad() > 0:
         self.processLoad()
         self.toWrite.append(self.getLoad())
         curTime = self.timer.time()
         if curTime > self.lastWrite + self.period:
            if len(self.toWrite) == 0:
               ld = 0
            else:
               ld = sum(self.toWrite) / len(self.toWrite)

            self.toWrite = []
            self.lastWrite = curTime

            self.outfile.write("{}\t{}\t{}\n".format(self.timer.time(), ld, ld / self.workCapacity))
            self.outfile.flush()
         
         self.timer.sleep(0.050)

      curTime = self.timer.time()
      if curTime > self.lastWrite + self.period:
         if len(self.toWrite) == 0:
            ld = 0
         else:
            ld = sum(self.toWrite) / len(self.toWrite)

         self.outfile.write("{}\t{}\t{}\n".format(curTime, ld, ld / self.workCapacity))
         self.outfile.flush()

      self.outfile.close()
      self.timer.threadDone()

   def stop(self):
      self.running = False

class ProcessorPool:
   def __init__(self, processors, Balancer, timer, period):
      self.numProcessors = sum([processor["count"] for processor in processors])
      self.processors = []
      
      count = 0
      for processor in processors:
         for num in xrange(processor["count"]):
            self.processors.append(Processor(count, processor["capability"], timer, period))
            count += 1
      
      self.balancer = Balancer(self)

   def getNumProcessors(self):
      return self.numProcessors

   def getProcessorCapabilites(self):
      caps = []
      for proc in self.processors:
         caps.append(proc.workCapacity)
      return caps

   def start(self):
      for processor in self.processors:
         processor.start()

   def stop(self):
      for processor in self.processors:
         processor.stop()

      for processor in self.processors:
         processor.join()

   def addLoad(self, request):
      self.processors[self.balancer.chooseProcessor(request.path)].addLoad(request.load)
      self.balancer.addActualRequestLoad(request)

class Request:
   def __init__(self, time, load, path):
      self.time = time
      self.load = load
      self.path = path

class RequestCreator:
   def __init__(self, requests):
      self.requests = requests
      self.total = sum([r["freq"] for r in requests])

   def pick(self):
      selection = int(self.total * uniform())
      for r in self.requests:
         if selection < r["freq"]:
            return r
         else:
            selection -= r["freq"]
      raise Exception

   def getRequests(self, time, count):
      tmp = []

      while count > 0:
         request = self.pick()
         tmp.append(Request(time + uniform(), request["avg"] + request["dev"] * randn(), request["path"]))
         count -= 1

      tmp.sort(key=lambda x: x.time)

      return tmp

def main():
   try:
      with open(sys.argv[1]) as infile:
         conf = json.load(infile)
   except Exception as e:
      print("Error reading input file: {}".format(e))
      return

   creator = RequestCreator(conf["requests"])

   if conf["real_time"]:
      timer = timers.RealTimeKeeper()
   else:
      count = 0
      for processor in conf["processors"]:
         count += processor["count"]

      timer = timers.SimulatedTimeKeeper(count + 1)

   pool = ProcessorPool(conf["processors"], getattr(balancers, conf["balancer"]), timer, float(conf["log_period"]))

   with open(conf["load"]) as loadFile:
      pool.start()
      limit = 1000000
      pendingRequests = deque()
      firstTime = -1

      line = loadFile.readline()
      while firstTime < 0 or len(pendingRequests) > 0:
         while len(line) > 0 and len(pendingRequests) < limit:
            vals = line.split("\t");
            pendingRequests.extend(creator.getRequests(int(vals[0]), int(float(vals[1]))))
            line = loadFile.readline()

         curTime = timer.time()
         if firstTime < 0:
            firstTime = curTime - pendingRequests[0].time

         while len(pendingRequests) > 0 and curTime >= firstTime + pendingRequests[0].time:
            pool.addLoad(pendingRequests.popleft())

         timer.sleep(0.125)

   timer.threadDone()
   pool.stop()

if __name__ == '__main__':
    main()
