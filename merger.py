import glob

longest = 0
sets = []
for fileName in glob.glob("*.log"):
   with open(fileName) as f:
      data = []
      for line in f:
         vals = line.split("\t")
         data.append([int(1000 * float(vals[0])), float(vals[1]), float(vals[2])])

      if len(data) > longest:
         longest = len(data)

      sets.append(data)

f = open("merged.txt", 'w')
count = len(sets)
for ndx in xrange(longest):
   sum1 = 0
   sum2 = 0
   mx2 = 0
   for p in sets:
      if ndx < len(p):
         sum1 += p[ndx][1]
         sum2 += p[ndx][2]
         if p[ndx][2] > mx2:
            mx2 = p[ndx][2]

   m1 = sum1 / count
   m2 = sum2 / count
   ss1 = 0
   ss2 = 0
   for p in sets:
      if ndx < len(p):
         ss1 += (p[ndx][1] - m1)**2
         ss2 += (p[ndx][2] - m2)**2

   f.write("{}\t{}\t{}\t{}\n".format(ndx, ss1, ss2, mx2/m2 - 1.0))

f.close()
   