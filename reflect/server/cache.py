# -*- coding: utf-8 -*-

import logging
import time

visualiseFilepath = None








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
    return self.keyOf(data) in self.hashtable

  def keyOf(self, data):
    return data

  def insert(self, data):
    if self.keyOf(data) in self.hashtable:
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
    if self.keyOf(data) in self.hashtable:
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

  def __len__(self):
    return len(self.q1) + len(self.q2)

  def __contains__(self, data):
    return data in self.q1 or data in self.q2

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



class CacheEntry(dict):
  """CacheEntry()

  Represents the cached data of a single clip.
  """



  def __init__(self, node, isRoot, isHotnode, precedesHotnode, rootDistance, isIndirection, traverseTime):
    super().__init__()

    self.age = 0
    self.node = node
    self.isRoot = isRoot
    self.isHotnode = isHotnode
    self.precedesHotnode = precedesHotnode
    self.rootDistance = rootDistance
    self.isIndirection = isIndirection
    self.associatedIndirections = []
    self.successors = {}
    self.traverseTime = traverseTime



  def discardFrame(self, n):
    """discardFrame(n)

    Discard the specific frame `n`, and return the exact number of bytes discarded.
    """

    discardedBytes = self[n].nbytes
    del self[n]

    return discardedBytes



  @property
  def priority(self):
    if self.isIndirection:
      return float("-inf")
    elif self.associatedIndirections:
      # An indirection of this node might have a higher priority than this node's raw priority, so find the maximum
      maxPriorityFromAssociatedIndirections = max([indirection.rawPriority for indirection in self.associatedIndirections])
      return max(self.rawPriority, maxPriorityFromAssociatedIndirections)
    else:
      return self.rawPriority



  @property
  def rawPriority(self):
    if (self.precedesHotnode and not self.isHotnode) or len(self.successors) < 1:
      return (1.0 + self.rootDistance + 100.0) / (2**self.age)
    else:
      return (1.0 + self.rootDistance) / (2**self.age)



class SpecialisedCacheEntry(CacheEntry):
  """SpecialisedCacheEntry()
  """



  def __init__(self, node, isRoot, isHotnode, precedesHotnode, rootDistance, isIndirection, traverseTime):
    super().__init__(node, isRoot, isHotnode, precedesHotnode, rootDistance, isIndirection, traverseTime)

    self.heldFrames = MiddleRecentlyUsedQueue()

  def __getitem__(self, key):
    val = dict.__getitem__(self, key)
    self.heldFrames.access(key)
    return val

  def __setitem__(self, key, val):
    self.heldFrames.insert(key)
    dict.__setitem__(self, key, val)

  def __delitem__(self, key):
    if key in self.heldFrames:
      raise KeyError("Tried to delete {} from the CacheEntry, but {} is still in the MiddleRecentlyUsedQueue. Its queue entry should be removed (e.g. popped) before attempting to discard the actual frame data.")
    dict.__delitem__(self, key)

  def __repr__(self):
    return "{}({})".format(type(self).__name__, dict.__repr__(self))

  def update(self, *args, **kwargs):
    for k, v in dict(*args, **kwargs).iteritems():
      self[k] = v



  def discardBytes(self, target):
    """discardBytes(target)

    Discard at least `target` bytes of data from this cache entry, and return the exact number
    of bytes discarded.
    """

    bytesDiscarded = 0
    while bytesDiscarded < target and len(self.heldFrames) > 0:
      n = self.heldFrames.popMiddle()

      # Using self[n] here would involve calling self.heldFrames.access(n), which would fail
      # because n has already been popped.
      bytesDiscarded += dict.__getitem__(self, n).nbytes

      del self[n]

    return bytesDiscarded



class SpecialisedPriorityQueue(object):
  """SpecialisedPriorityQueue()

  Keeps track of clips in the cache in ascending order of their priority.
  """



  def __init__(self, cache):
    self._cacheEntries = sorted(cache.values(), key = lambda entry: entry.priority)

    # Create a map from cache entries to their index in the priority queue
    self._cacheEntryIndices = {}
    for i in range(len(self._cacheEntries)):
      self._cacheEntryIndices[id(self._cacheEntries[i])] = i

    # Find the index of the leftmost lowest-priority nonempty cache entry
    self._victimIndex = None
    self.findNewVictim(start = 0)



  def peek(self):
    if self._victimIndex is not None:
      return self._cacheEntries[self._victimIndex]
    else:
      return None



  def findNewVictim(self, start = None):
    # Find the index of the leftmost lowest-priority nonempty cache entry
    if start is not None:
      i = start
    else:
      i = self._victimIndex

    while i < len(self._cacheEntries) and len(self._cacheEntries[i]) == 0:
      i += 1

    if i < len(self._cacheEntries):
      # A nonempty cache entry was found; this will be the first victim
      self._victimIndex = i
    else:
      self._victimIndex = None



  def setVictim(self, cacheEntry):
    newVictimIndex = self._cacheEntryIndices[id(cacheEntry)]
    if self._victimIndex is not None and self.peek().priority == cacheEntry.priority:
      # Ensure the new victim is the *leftmost* cache entry of this priority
      self._victimIndex = min(self._victimIndex, newVictimIndex)
    else:
      self._victimIndex = newVictimIndex











































































class Cache:
  """Cache()

  This class can hold various kinds of cachable data (currently only numpy images).
  Data is "staged" for caching by the `stage` method.
  Calling the `commit` method will run the cache algorithm, which may result in some cached data
    being discarded and some staged data being added.
  Data is retrieved (from either the main cache or the temporary staging area) by the `get` method.

  At any point in time, there is exactly one active cache, accessible via the static
  `current` method. Usually it can be left untouched, but it may be swapped in order to enable
  advanced manipulation of multiple distinct caches.
  """



  @staticmethod
  def current():
    return globals()["currentCache"]



  @staticmethod
  def swap(newCache):
    """swap(newCache)

    Set the current global cache to `newCache`, and return the old cache.
    """

    oldCache = globals()["currentCache"]
    globals()["currentCache"] = newCache
    return oldCache



  def __init__(self, maxSize, enableStatistics = False):
    # These two-level dicts implement functions (clip → n → data).
    # They are expected (but not strictly required) to be disjoint, i.e.
    #   (n in committed[clip]) -> not(n in staged[clip]),
    #   (n in staged[clip])    -> not(n in committed[clip]).
    self._committed = {} # Persistent store
    self._staged = {}    # Temporary staging area, emptied at the end of script execution

    self._priorityQueue = None

    self.userScriptIsRunning = False # Determines which store to send incoming frames to

    self._stagingAreaIsLocked = False # Can be locked to temporarily prevent any frames from being staged

    self._currentSize = 0
    self.maxSize = maxSize

    self._enableStatistics = enableStatistics

    # For evaluation
    self.resetStats()
    self.CacheEntryImplementation = CacheEntry



  def __str__(self):
    stagedBins = []
    stagedClips = len(self._staged)
    stagedFrames = 0
    stagedBytes = 0
    for clip, entry in self._staged.items():
      h = clip.__hash__()
      if h not in stagedBins:
        stagedBins.append(h)
      stagedFrames += len(entry)
      for n, image in entry.items():
        stagedBytes += image.nbytes

    committedBins = []
    committedClips = len(self._committed)
    committedFrames = 0
    committedBytes = 0
    for clip, entry in self._committed.items():
      h = clip.__hash__()
      if h not in committedBins:
        committedBins.append(h)
      committedFrames += len(entry)
      for n, image in entry.items():
        committedBytes += image.nbytes

    return "<{}: ({} frames, {} MiB) staged / ({} bins, {} clips, {} frames, {} MiB) committed>".format(
      type(self).__name__,
      # len(stagedBins),
      # stagedClips,
      stagedFrames,
      round(stagedBytes / 1024 / 1024, 1),
      len(committedBins),
      committedClips,
      committedFrames,
      round(committedBytes / 1024 / 1024, 1)
    )



  def stats(self):
    if not self._enableStatistics:
      return "Stats are not being collected; use --collectStatistics to enable stats"

    denominator = self._stats["hits"] + self._stats["misses"]["noncompulsory"]
    if denominator != 0:
      hitRatio = round(self._stats["hits"] / denominator, 5)
    else:
      hitRatio = "inf"

    return "Cache stats: {} h / {} ncm / {} cm / {} hr".format(
      self._stats["hits"],
      self._stats["misses"]["noncompulsory"],
      self._stats["misses"]["compulsory"],
      hitRatio
    )



  def resetStats(self):
    self._stats = {
      "hits": 0,
      "misses": {
        "compulsory": 0,
        "noncompulsory": 0
      },
      "seenFrames": {}
    }



  def hit(self, cacheEntry, n):
    if self._enableStatistics:
      if not cacheEntry.isIndirection:
        self._stats["hits"] += 1



  def miss(self, cacheEntry, n):
    if self._enableStatistics:
      if not cacheEntry.isIndirection:
        if (id(cacheEntry), n) in self._stats["seenFrames"]:
          self._stats["misses"]["noncompulsory"] += 1
        else:
          self._stats["misses"]["compulsory"] += 1



  def seenFrame(self, cacheEntry, n):
    if self._enableStatistics:
      self._stats["seenFrames"][(id(cacheEntry), n)] = True



  def explicitChecker(f):
    varnames = f.__code__.co_varnames
    def wrapper(*a, **kw):
      kw["explicitParams"] = set(list(varnames[:len(a)]) + list(kw.keys()))
      return f(*a, **kw)
    return wrapper

  @explicitChecker
  def get(self, clip, n, default = None, explicitParams = None):
    # Check the staging area
    if clip in self._staged:
      if n in self._staged[clip]:
        return self._staged[clip][n]

    # Check the persistent store
    cacheEntry = clip.cacheEntry
    if cacheEntry is not None and n in cacheEntry:
      self.hit(cacheEntry, n)
      return cacheEntry[n]

    # The sought data is neither cached nor staged for caching.
    self.miss(cacheEntry, n)
    if "default" in explicitParams:
      return default
    else:
      raise KeyError((clip, n))



  def lockStagingArea(self):
    if self._stagingAreaIsLocked:
      raise Exception("Attempted to lock the staging area, but it was already locked")
    else:
      self._stagingAreaIsLocked = True



  def unlockStagingArea(self):
    if not self._stagingAreaIsLocked:
      raise Exception("Attempted to unlock the staging area, but it was already unlocked")
    else:
      self._stagingAreaIsLocked = False



  def set(self, clip, n, data):
    if clip.cacheEntry is not None:
      self.seenFrame(clip.cacheEntry, n)



  def stage(self, clip, n, data):
    if clip in self._staged:
      self._staged[clip][n] = data
    else:
      self._staged[clip] = { n: data }



  def emptyStagingArea(self):
    self._staged = {}



  def commit(self):
    if self.userScriptIsRunning:
      raise Exception("Attempted to commit staged frames while a user script is still running")

    # For each staged piece of data, either move it to the main cache or discard it (depending on its priority)
    for clip, stagedEntry in self._staged.items():
      if clip.cacheEntry is None:
        # Each node in the DAG should have a cache entry after the reprioritisation stage.
        # The exception to this is resize nodes, which may have fused/annihilated with the special
        # resize done to fit the clip within the preview window.
        # In this case, `clip` is no longer in the DAG so its staged frames will not be used; they
        # can therefore be safely discarded.
        continue
      for n, data in stagedEntry.items():
        self.set(clip, n, data)
    self._staged = {}



  def _setUpPriorities(self, graph):
    raise NotImplementedError()



  def reprioritise(self, graph):
    """reprioritise(graph)

    Update the priorities of each clip in the main cache, according to the given composition graph.
    0. Dampening:     Reduce the priorities of cache entries of clips not in `graph`
    1. Root distance: Set priorities of cache entries of clips in `graph` according to the clip's
                      maximum distance from the root
    2. Hotnodes:      Boost priorities of predecessors of hotnodes ("new" cache entries)

    Preconditions:
    * Every `clip` in `graph` must satisfy "clip.cacheEntry is None", i.e. this graph hasn't been
      used in a previous reprioritise call.

    Side effects:
    * Each clip in `graph` has a `cacheEntry` property pointing to its entry in the cache.
    * Each clip in `graph` has a new dict property `indirectionsTakenCareOf` (which can be ignored).
    """

    t1 = time.perf_counter()

    # Ensure that the precondition is met
    for leaf in graph.leaves:
      if leaf.cacheEntry is not None:
        logging.warn("Attempted to reprioritise using a graph that has already been used to reprioritise.")
        return
      break

    # Sweep over the whole cache, incrementing each age counter (which will dampen priorities)
    for node, cacheEntry in self._committed.items():
      cacheEntry.age += 1

    # Post-order graph traversal starting from the leaves
    N = [0] # debug counter
    traverseTime = [time.time()]
    def traverse(node):
      if node.cacheEntry is not None:
        # This node has already been visited
        return node.cacheEntry
      else:
        N[0] += 1
        if isinstance(node._source, str) or node._source is None:
          # This node is a root
          cacheEntry = self._committed.get(node, None)
          if cacheEntry is None:
            cacheEntry = self.CacheEntryImplementation(node = node, isRoot = True, isHotnode = True, precedesHotnode = False, rootDistance = 0, isIndirection = node.isIndirection, traverseTime = traverseTime[0])
            self._committed[node] = cacheEntry
          elif cacheEntry.traverseTime != traverseTime[0]: # Avoid updating the same cacheEntry more than once during this reprioritisation
            cacheEntry.isRoot = True
            cacheEntry.isHotnode = (cacheEntry.age > 1) # True iff the node was not in the previous graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = 0
            cacheEntry.isIndirection = node.isIndirection
            cacheEntry.associatedIndirections = []
            cacheEntry.age = 0
            cacheEntry.traverseTime = traverseTime[0]
        elif isinstance(node._source, tuple):
          # First visit this node's sources
          sourceCacheEntries = []
          for source in node._source:
            sourceCacheEntry = traverse(source)
            sourceCacheEntries.append(sourceCacheEntry)

          # To retrieve the current node's cacheEntry (if it exists), we could just call:
          # cacheEntry = self._committed.get(node, None)
          # However, this will involve O(d²) calls to Clip.__eq__ if the graph has depth d.
          # A more efficient method is to make use of the source nodes' cacheEntries, which will
          #   all point to the current node's cacheEntry if it exists.
          def intersect(ds):
            if len(ds) == 0:
              return []
            else:
              return [v for k, v in ds[0].items() if all(k in d for d in ds[1:])]
          candidateCacheEntries = intersect([e.successors[node.__hash__()] for e in sourceCacheEntries if node.__hash__() in e.successors])
          chosenCacheEntries = [e for e in candidateCacheEntries if node._pseudoeq(e.node)]
          if len(chosenCacheEntries) == 0:
            cacheEntry = None
          elif len(chosenCacheEntries) == 1:
            cacheEntry = chosenCacheEntries[0]
          else:
            raise Exception("Duplicate cache entries found for {}".format(node))

          # Update the predecessors if this node is hot, and determine the maximum distance from a root to this node
          maxRootDistance = None
          for sourceCacheEntry in sourceCacheEntries:
            if cacheEntry is None or cacheEntry.age > 1:
              # This node is hot, so we need to update the entry of the predecessor
              sourceCacheEntry.precedesHotnode = True
            if maxRootDistance is None or sourceCacheEntry.rootDistance > maxRootDistance:
              maxRootDistance = sourceCacheEntry.rootDistance

          if cacheEntry is None:
            cacheEntry = self.CacheEntryImplementation(node = node, isRoot = False, isHotnode = True, precedesHotnode = False, rootDistance = maxRootDistance + 1, isIndirection = node.isIndirection, traverseTime = traverseTime[0])
            self._committed[node] = cacheEntry
          elif cacheEntry.traverseTime != traverseTime[0]: # Avoid updating the same cacheEntry more than once during this reprioritisation
            cacheEntry.isRoot = False
            cacheEntry.isHotnode = (cacheEntry.age > 1) # True iff the node was not in the previous graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = maxRootDistance + 1
            cacheEntry.isIndirection = node.isIndirection
            cacheEntry.associatedIndirections = []
            cacheEntry.age = 0
            cacheEntry.traverseTime = traverseTime[0]

          # Make sure the source cacheEntries (predecessors) know that this cacheEntry is one of their successors.
          for sourceCacheEntry in sourceCacheEntries:
            if node.__hash__() not in sourceCacheEntry.successors:
              sourceCacheEntry.successors[node.__hash__()] = {}
            if id(cacheEntry) not in sourceCacheEntry.successors[node.__hash__()]:
              sourceCacheEntry.successors[node.__hash__()][id(cacheEntry)] = cacheEntry

        node.cacheEntry = cacheEntry
        node.indirectionsTakenCareOf = []
        return cacheEntry
    for leaf in graph.leaves:
      traverse(leaf)

    # In the case when an indirection I has high priority, and the nodes N that it is an
    # indirection of have low raw priority, the nodes N need to know that their effective priority
    # should in fact be that of I. This is achieved by assigning to each cache entry a list
    # (`associatedIndirections`) from which it can work out the maximum priority.
    M = [0] # debug counter
    def associateIndirections(node, indirections):
      if isinstance(node._source, str) or node._source is None:
        # The node is a root
        node.cacheEntry.associatedIndirections.extend(indirections.values())
      elif isinstance(node._source, tuple):
        M[0] += 1
        if node.cacheEntry.isIndirection:
          # Add this node's cache entry to the accumulating list of indirections if necessary,
          # and recurse.
          if not node.indirectionsTakenCareOf:
            indirections = indirections.copy()
            indirections[id(node.cacheEntry)] = node.cacheEntry
            node.indirectionsTakenCareOf = indirections.copy()
          else:
            # Remove any indirections from the current list that have already been taken care of
            # by a previous visit to this node.
            indirectionIdsToDelete = []
            for indirectionId, indirection in indirections.items():
              if indirectionId in node.indirectionsTakenCareOf:
                indirectionIdsToDelete.append(indirectionId)
              else:
                node.indirectionsTakenCareOf[indirectionId] = indirection
            for indirectionId in indirectionIdsToDelete:
              del indirections[indirectionId]
            if not indirections:
              # This node and any subsequent indirections have already been taken care of, and there
              # is nothing in the current indirections list to be carried along in the recursion, so
              # we can stop here.
              return
          for source in node._source:
            associateIndirections(source, indirections)
        else:
          # This node is not an indirection, so set its associated indirections list.
          node.cacheEntry.associatedIndirections.extend(indirections.values())
          # A predecessor of this node may be an indirection, so if it hasn't already been taken
          # care of then begin the recursion again from this node.
          if not node.indirectionsTakenCareOf:
            node.indirectionsTakenCareOf = indirections.copy()
            for source in node._source:
              associateIndirections(source, {})
    for leaf in graph.leaves:
      associateIndirections(leaf, {})

    # Get rid of cache entries that are old, empty, and have low priority
    minimumPriority = 0.5 # Magic number
    maximumAge = 5 # Magic number
    clipsToPurge = []
    for clip, cacheEntry in self._committed.items():
      if cacheEntry.age > maximumAge and len(cacheEntry) == 0 and cacheEntry.priority < minimumPriority:
        clipsToPurge.append((clip, cacheEntry))
    for clip, cacheEntry in clipsToPurge:
      # Remove any references to this cacheEntry from cacheEntries of this node's sources
      if isinstance(clip._source, tuple):
        for source in clip._source:
          if id(cacheEntry) in source.cacheEntry.successors[clip.__hash__()]:
            del source.cacheEntry.successors[clip.__hash__()][id(cacheEntry)]

      # Remove the (clip, cacheEntry) item from the master dict
      del self._committed[clip]

    self._setUpPriorities()

    t2 = time.perf_counter()
    logging.info("Reprioritised {} nodes in {} s".format(N[0], t2 - t1))

    # Debug
    if visualiseFilepath is not None:
      logging.info("Writing graph visualisation to {}".format(visualiseFilepath))
      self.visualisePriorities(graph, visualiseFilepath)
      logging.info("Wrote graph visualisation to {}".format(visualiseFilepath))



  def visualisePriorities(self, graph, filepath):
    import pydotplus

    G = pydotplus.Dot(graph_type = "digraph")

    visited = {}
    i = [1000]
    def traverse(node, pydotSuccessor):
      i[0] += 1
      if node in visited:
        pydotNode = visited[node]
        G.add_edge(pydotplus.Edge(pydotNode, pydotSuccessor))
      else:
        keyNode = None
        for potentialKey in self._committed:
          if potentialKey == node:
            keyNode = potentialKey
            break
        if node.cacheEntry.isHotnode:
          fillColour = "#ff5555"
        elif node.cacheEntry.precedesHotnode:
          fillColour = "#8888ff"
        else:
          fillColour = "#ffffff"
        notCacheable = node.cacheEntry.isIndirection
        extra = ""
        from reflect.core import vfx
        if isinstance(keyNode, vfx.subclip.SubVideoClip):
          extra = "[{}, {}]".format(keyNode._n1, keyNode._n2)
        pydotNode = pydotplus.Node("{}{}\np={}\nn={}\niI={}\niC={}\nch={}\n{}".format(
          keyNode,
          i[0],
          round(self._committed[keyNode].priority, 1),
          "N/A ({})".format(len(self._committed[keyNode])) if notCacheable else len(self._committed[keyNode]),
          node.cacheEntry.isIndirection,
          node._isConstant,
          node._childCount,
          extra
        ), style = "filled", fillcolor = fillColour)
        G.add_node(pydotNode)
        visited[node] = pydotNode
        if pydotSuccessor is not None:
          G.add_edge(pydotplus.Edge(pydotNode, pydotSuccessor))
        if isinstance(node._source, tuple):
          for source in node._source:
            traverse(source, pydotNode)

    for leaf in graph.leaves:
      traverse(leaf, None)

    for node in self._committed:
      if node not in visited:
        i[0] += 1
        # G.add_node(pydotplus.Node("{}{}, p={}".format(node, i[0], round(node.cacheEntry.priority, 1)), style = "filled", fillcolor = "#aaaaaa"))

    G.write_png(filepath)



class SpecialisedCache(Cache):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.CacheEntryImplementation = SpecialisedCacheEntry

  def set(self, clip, n, data):
    super().set(clip, n, data)

    if self.userScriptIsRunning:
      if not self._stagingAreaIsLocked:
        self.stage(clip, n, data)
    else:
      if clip.isIndirection:
        # There's no point in caching this data, so reject it immediately
        return
      while self._currentSize + data.nbytes > self.maxSize and self._priorityQueue.peek() is not None and self._priorityQueue.peek().priority <= clip.cacheEntry.priority:
        # There isn't room in the cache, but there exists some cached data with a lower priority than the candidate clip's
        victim = self._priorityQueue.peek()
        totalFreedBytes = victim.discardBytes(self._currentSize + data.nbytes - self.maxSize)
        self._currentSize -= totalFreedBytes
        if len(victim) == 0:
          # All of the victim's data has been discarded
          self._priorityQueue.findNewVictim()
      if self._currentSize + data.nbytes <= self.maxSize:
        # Add the data to the cache and ensure the priority queue knows the correct next victim
        clip.cacheEntry[n] = data
        self._currentSize += data.nbytes
        currentVictim = self._priorityQueue.peek()
        if currentVictim is None or currentVictim.priority >= clip.cacheEntry.priority:
          self._priorityQueue.setVictim(clip.cacheEntry)

  def _setUpPriorities(self):
    # Replace the priority queue
    self._priorityQueue = SpecialisedPriorityQueue(self._committed)



class FIFOCache(Cache):

  def set(self, clip, n, data):
    super().set(clip, n, data)

    if self.userScriptIsRunning:
      if not self._stagingAreaIsLocked:
        self.stage(clip, n, data)
    else:
      if clip.isIndirection:
        # There's no point in caching this data, so reject it immediately
        return
      while self._currentSize + data.nbytes > self.maxSize and len(self._priorityQueue) > 0:
        (victim, frameToDiscard) = self._priorityQueue.pop(0)
        # print("discarding {}/{}".format(victim.node, frameToDiscard))
        totalFreedBytes = victim.discardFrame(frameToDiscard)
        self._currentSize -= totalFreedBytes
      if self._currentSize + data.nbytes <= self.maxSize:
        # print("caching {}/{}".format(clip, n))
        clip.cacheEntry[n] = data
        self._currentSize += data.nbytes
        self._priorityQueue.append((clip.cacheEntry, n))

  def _setUpPriorities(self):
    if self._priorityQueue is None:
      self._priorityQueue = []



class LRUCache(Cache):

  class LeastRecentlyUsedQueue(RecentlyUsedQueue):

    def keyOf(self, data):
      cacheEntry, n = data
      return (id(cacheEntry), n)

    def __str__(self):
      victims = []
      current = self.head
      while current is not None:
        e, n = current.data
        victims.append("{}{}".format(type(e.node).__name__[0], n))
        current = current.next
      return str(victims)

  def hit(self, cacheEntry, n):
    super().hit(cacheEntry, n)
    self._priorityQueue.access((cacheEntry, n))

  def set(self, clip, n, data):
    super().set(clip, n, data)

    if self.userScriptIsRunning:
      if not self._stagingAreaIsLocked:
        self.stage(clip, n, data)
    else:
      if clip.isIndirection:
        # There's no point in caching this data, so reject it immediately
        return
      while self._currentSize + data.nbytes > self.maxSize and not self._priorityQueue.isEmpty():
        (victim, frameToDiscard) = self._priorityQueue.popTail()
        # print("discarding {}/{}".format(victim.node, frameToDiscard))
        totalFreedBytes = victim.discardFrame(frameToDiscard)
        self._currentSize -= totalFreedBytes
      if self._currentSize + data.nbytes <= self.maxSize:
        # print("caching {}/{}".format(clip, n))
        clip.cacheEntry[n] = data
        self._currentSize += data.nbytes
        self._priorityQueue.insert((clip.cacheEntry, n))

  def _setUpPriorities(self):
    if self._priorityQueue is None:
      self._priorityQueue = self.LeastRecentlyUsedQueue()



class MRUCache(Cache):

  class MostRecentlyUsedQueue(RecentlyUsedQueue):

    def keyOf(self, data):
      cacheEntry, n = data
      return (id(cacheEntry), n)

    def __str__(self):
      victims = []
      current = self.head
      while current is not None:
        e, n = current.data
        victims.append("{}{}".format(type(e.node).__name__[0], n))
        current = current.next
      return str(victims)

  def hit(self, cacheEntry, n):
    super().hit(cacheEntry, n)
    self._priorityQueue.access((cacheEntry, n))

  def set(self, clip, n, data):
    super().set(clip, n, data)

    if self.userScriptIsRunning:
      if not self._stagingAreaIsLocked:
        self.stage(clip, n, data)
    else:
      if clip.isIndirection:
        # There's no point in caching this data, so reject it immediately
        return
      while self._currentSize + data.nbytes > self.maxSize and not self._priorityQueue.isEmpty():
        (victim, frameToDiscard) = self._priorityQueue.popHead()
        # print("discarding {}/{}".format(victim.node, frameToDiscard))
        totalFreedBytes = victim.discardFrame(frameToDiscard)
        self._currentSize -= totalFreedBytes
      if self._currentSize + data.nbytes <= self.maxSize:
        # print("caching {}/{}".format(clip, n))
        clip.cacheEntry[n] = data
        self._currentSize += data.nbytes
        self._priorityQueue.insert((clip.cacheEntry, n))

  def _setUpPriorities(self):
    if self._priorityQueue is None:
      self._priorityQueue = self.MostRecentlyUsedQueue()



# Initialise an empty cache
currentCache = SpecialisedCache(100 * 1024 * 1024) # 100 MiB
