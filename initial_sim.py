from collections import deque
from heapq import heappush, heappop
from numpy.random import randn, uniform
import sys
import time

def randVal(sigma, mu):
   return sigma * randn() + mu

def addRecord(requests, line):
   mu = 0.25
   sigma = 0.1

   vals = line.split("\t");
   time = int(vals[0])
   count = int(float(vals[1]))
   tmp = []
   while count > 0:
      offset = time + uniform()
      tmp.append((offset, offset + abs(randVal(sigma, mu))))
      #heappush(tmp, (offset, offset + abs(randVal(sigma, mu))))
      #heappush(tmp, (time, time + 1))
      count -= 1
   #requests.extend([heappop(tmp) for i in range(len(tmp))])
   tmp.sort()
   requests.extend(tmp)

with open(sys.argv[1]) as loadFile:
   limit = 1000000
   pendingRequests = deque()
   currentRequests = deque()
   firstTime = -1

   line = loadFile.readline()
   while firstTime < 0 or len(pendingRequests) > 0 or len(currentRequests) > 0:
      while len(line) > 0 and len(pendingRequests) < limit:
         addRecord(pendingRequests, line)
         line = loadFile.readline()

      curTime = time.time()
      if firstTime < 0:
         firstTime = curTime - pendingRequests[0][0]

      while len(currentRequests) > 0 and curTime >= firstTime + currentRequests[0]:
         #heappop(currentRequests)
         currentRequests.popleft()

      while len(pendingRequests) > 0 and curTime >= firstTime + pendingRequests[0][0]:
         #heappush(currentRequests, heappop(pendingRequests)[1])
         currentRequests.append(pendingRequests.popleft()[1])

      sys.stdout.write("\r\x1b[K"+str(curTime - firstTime) + "\t" + str(len(currentRequests)))
      sys.stdout.flush()
      time.sleep(0.125)
   print ""
