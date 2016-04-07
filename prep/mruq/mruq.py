
class RecentlyUsedQueue(object):

  class Victim(object):
    def __init__(self, data, next = None, prev = None):
      self.data = data
      self.next = next
      self.prev = prev

  def __init__(self):
    self.head = None
    self.tail = None
    self.hashtable = {}

  def __len__(self):
    return len(self.hashtable)

  def __contains__(self, data):
    return data in self.hashtable

  def keyOf(self, data):
    return data

  def insert(self, data):
    if data in self.hashtable:
      raise ValueError("Tried to insert {} into the RecentlyUsedQueue, but it was already there")
    if self.head is None:
      victim = self.Victim(data)
      self.head = victim
      self.tail = victim
    else:
      victim = self.Victim(data, self.head)
      self.head = victim
      victim.next.prev = victim
    self.hashtable[self.keyOf(data)] = victim
    return victim

  def append(self, data):
    if data in self.hashtable:
      raise ValueError("Tried to append {} to the RecentlyUsedQueue, but it was already there")
    if self.tail is None:
      victim = self.Victim(data)
      self.head = victim
      self.tail = victim
    else:
      victim = self.Victim(data, None, self.tail)
      self.tail = victim
      victim.prev.next = victim
    self.hashtable[self.keyOf(data)] = victim
    return victim

  def access(self, data):
    victim = self.hashtable.get(self.keyOf(data), None)
    if victim is None:
      self.insert(data)
    else:
      # Move it to the front
      if victim.prev is None:
        pass
      else:
        victim.prev.next = victim.next
        if victim.next is None:
          self.tail = victim.prev
        else:
          victim.next.prev = victim.prev
        victim.prev = None
        victim.next = self.head
        self.head.prev = victim
        self.head = victim

  def delete(self, data):
    victim = self.hashtable[self.keyOf(data)]

    if victim.next is None:
      if victim.prev is None:
        self.head = None
        self.tail = None
      else:
        victim.prev.next = None
        self.tail = victim.prev
    else:
      if victim.prev is None:
        victim.next.prev = None
        self.head = victim.next
      else:
        victim.prev.next = victim.next
        victim.next.prev = victim.prev

    del self.hashtable[self.keyOf(data)]

  def __str__(self):
    victims = []
    current = self.head
    while current is not None:
      victims.append(current.data)
      current = current.next
    return str(victims)

  def popHead(self):
    if self.isEmpty():
      raise KeyError()

    victim = self.head
    if victim.next is None:
      self.head = None
      self.tail = None
    else:
      self.head = victim.next
      victim.next.prev = None

    del self.hashtable[self.keyOf(victim.data)]

    return victim.data

  def popTail(self):
    if self.isEmpty():
      raise KeyError()

    victim = self.tail
    if victim.prev is None:
      self.head = None
      self.tail = None
    else:
      self.tail = victim.prev
      victim.prev.next = None

    del self.hashtable[self.keyOf(victim.data)]

    return victim.data

  def isEmpty(self):
    return self.head is None



class MiddleRecentlyUsedQueue(object):

  def __init__(self):
    self.q1 = RecentlyUsedQueue()
    self.q2 = RecentlyUsedQueue()

  @property
  def head(self):
    return self.q1.head

  @property
  def middle(self):
    return self.q2.head

  @property
  def tail(self):
    return self.q2.tail

  def recoverInvariant(self):
    print((len(self.q1), len(self.q2)))
    # Adjust
    if len(self.q1) >= len(self.q2) + 1:
      # Shift q1's tail to q2's head
      self.q2.insert(self.q1.tail.data)
      self.q1.delete(self.q1.tail.data)
    elif len(self.q1) == len(self.q2) - 2:
      # Shift q2's head to q1's tail
      self.q1.append(self.q2.head.data)
      self.q2.delete(self.q2.head.data)

    # Check invariant
    if len(self.q1) > len(self.q2) + 1 or len(self.q1) < len(self.q2) - 1:
      raise Exception()

  def keyOf(self, data):
    return data

  def insert(self, data):
    if data in self.q1:
      raise ValueError("Tried to insert {} into the MiddleRecentlyUsedQueue, but it was already there")
    elif data in self.q2:
      raise ValueError("Tried to insert {} into the MiddleRecentlyUsedQueue, but it was already there")
    else:
      self.q1.insert(data)

      self.recoverInvariant()

  def append(self, data):
    if data in self.q1:
      raise ValueError("Tried to append {} to the MiddleRecentlyUsedQueue, but it was already there")
    elif data in self.q2:
      raise ValueError("Tried to append {} to the MiddleRecentlyUsedQueue, but it was already there")
    else:
      self.q2.append(data)

      self.recoverInvariant()

  def access(self, data):
    if data in self.q1:
      self.q1.access(data)
    elif data in self.q2:
      self.q2.delete(data)
      self.q1.insert(data)
      self.recoverInvariant()
    else:
      raise KeyError(data)

  def delete(self, data):
    if data in self.q1:
      self.q1.delete(data)
    elif data in self.q2:
      self.q2.delete(data)
    else:
      raise KeyError(data)

    self.recoverInvariant()

  def __str__(self):
    return "q1: {}\nq2: {}".format(self.q1, self.q2)

  def popHead(self):
    data = self.q1.popHead()

    self.recoverInvariant()

    return data

  def popMiddle(self):
    data = self.q2.popHead()

    self.recoverInvariant()

    return data

  def popTail(self):
    data = self.q2.popTail()

    self.recoverInvariant()

    return data

  def isEmpty(self):
    return self.head is None





q = MiddleRecentlyUsedQueue()
print("{}\n".format(q))

q.insert(1)
print("{}\n".format(q))
q.insert(2)
print("{}\n".format(q))
q.insert(3)
print("{}\n".format(q))
q.insert(4)
print("{}\n".format(q))
q.insert(5)
print("{}\n".format(q))

print(q.popMiddle())
print("{}\n".format(q))
print(q.popMiddle())
print("{}\n".format(q))
print(q.popMiddle())
print("{}\n".format(q))
print(q.popMiddle())
print("{}\n".format(q))
print(q.popMiddle())
print("{}\n".format(q))

q.insert(3)
print("{}\n".format(q))
q.insert(2)
print("{}\n".format(q))
q.insert(4)
print("{}\n".format(q))
q.insert(1)
print("{}\n".format(q))

q.access(3)
print("{}\n".format(q))
q.insert(6)
print("{}\n".format(q))
q.delete(2)
print("{}\n".format(q))
q.delete(4)
print("{}\n".format(q))
q.access(1)
print("{}\n".format(q))

q.insert(2)
print("{}\n".format(q))
q.insert(4)
print("{}\n".format(q))


