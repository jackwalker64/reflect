
import time
from functools import reduce

def measure():
  t0 = time.time()
  t1 = t0
  while t1 == t0:
    t1 = time.time()
  return (t0, t1, t1-t0)

# samples = [measure() for i in range(10)]

# for s in samples:
#   print(s)

print(reduce( lambda a,b:a+b, [measure()[2] for i in range(1000)], 0.0) / 1000.0)


def measure_clock():
  t0 = time.clock()
  t1 = time.clock()
  while t1 == t0:
    t1 = time.clock()
  return (t0, t1, t1-t0)

x = reduce( lambda a,b:a+b, [measure_clock()[2] for i in range(1000000)] )/1000000.0
print(x)



def measure_perf():
  t0 = time.perf_counter()
  t1 = time.perf_counter()
  while t1 == t0:
    t1 = time.perf_counter()
  return (t0, t1, t1-t0)

x = reduce( lambda a,b:a+b, [measure_perf()[2] for i in range(1000000)] )/1000000.0
print(x*1000000)
