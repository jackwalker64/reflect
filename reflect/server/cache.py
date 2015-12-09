# -*- coding: utf-8 -*-



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



  def __init__(self, maxSize):
    # These two-level dicts implement functions (clip → n → data).
    # They are expected (but not strictly required) to be disjoint, i.e.
    #   (n in committed[clip]) -> not(n in staged[clip]),
    #   (n in staged[clip])    -> not(n in committed[clip]).
    self._committed = {} # Persistent store
    self._staged = {}    # Temporary staging area, emptied at the end of script execution

    self._priorityQueue = None

    self.userScriptIsRunning = False # Determines which store to send incoming frames to

    self._currentSize = 0
    self.maxSize = maxSize



  def __str__(self):
    stagedClips = len(self._staged)
    stagedFrames = 0
    stagedBytes = 0
    for clip, entry in self._staged.items():
      stagedFrames += len(entry)
      for n, image in entry.items():
        stagedBytes += image.nbytes

    committedClips = len(self._committed)
    committedFrames = 0
    committedBytes = 0
    for clip, entry in self._committed.items():
      committedFrames += len(entry)
      for n, image in entry.items():
        committedBytes += image.nbytes

    return "<cache: ({} clips, {} frames, {} MiB) staged / ({} clips, {} frames, {} MiB) committed>".format(
      # "{}.{}".format(self.__module__, self.__class__.__name__),
      stagedClips,
      stagedFrames,
      round(stagedBytes / 1024 / 1024, 1),
      committedClips,
      committedFrames,
      round(committedBytes / 1024 / 1024, 1)
    )



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
    if clip in self._committed:
      if n in self._committed[clip]:
        return self._committed[clip][n]

    # The sought data is neither cached nor staged for caching.
    if "default" in explicitParams:
      return default
    else:
      raise KeyError((clip, n))



  def set(self, clip, n, data):
    if self.userScriptIsRunning:
      self.stage(clip, n, data)
    else:
      while self._currentSize + data.nbytes > self.maxSize and self._priorityQueue.peek().priority < clip.cacheEntry.priority:
        # There isn't room in the cache, but there exists some cached data with a lower priority than the candidate clip's
        victim = self._priorityQueue.peek()
        totalFreedBytes = victim.discardBytes(self._currentSize + data.nbytes - self.maxSize)
        self._currentSize -= totalFreedBytes
        if len(victim) == 0:
          # All of the victim's data has been discarded
          self._priorityQueue.findNewVictim()
      if self._currentSize + data.nbytes <= self.maxSize:
        # Add the data to the cache and ensure the priority queue knows the correct next victim
        self._committed[clip][n] = data
        self._currentSize += data.nbytes
        currentVictim = self._priorityQueue.peek()
        if currentVictim is None or currentVictim.priority > clip.cacheEntry.priority:
          self._priorityQueue.findNewVictim(start = 0) # TODO: Improve efficiency by instead implementing pq.setVictim(clip.cacheEntry)



  def stage(self, clip, n, data):
    if clip in self._staged:
      self._staged[clip][n] = data
    else:
      self._staged[clip] = { n: data }



  def commit(self):
    # For each staged frame, either move it to the main cache or discard it (depending on its priority)
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
    """

    # Sweep over the whole cache, incrementing each age counter (which will dampen priorities)
    for node, cacheEntry in self._committed.items():
      cacheEntry.age += 1

    # Post-order graph traversal starting from the leaves
    def traverse(node):
      if node.cacheEntry is not None:
        # This node has already been visited
        return node.cacheEntry
      else:
        if isinstance(node._source, str):
          # This node is a root
          cacheEntry = self._committed.get(node, None)
          if cacheEntry is None:
            cacheEntry = CacheEntry(isRoot = True, isHotnode = True, precedesHotnode = False, rootDistance = 0)
            self._committed[node] = cacheEntry
          else:
            cacheEntry.isRoot = True
            cacheEntry.isHotnode = (cacheEntry.age > 1) # True iff the node was not in the previous graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = 0
            cacheEntry.age = 0
        elif isinstance(node._source, tuple):
          cacheEntry = self._committed.get(node, None)

          # First visit this node's sources
          maxRootDistance = None
          for source in node._source:
            sourceCacheEntry = traverse(source)
            if cacheEntry is None or cacheEntry.age > 1:
              # This node is hot, so we need to update the entry of the predecessor
              sourceCacheEntry.precedesHotnode = True
            if maxRootDistance is None or sourceCacheEntry.rootDistance > maxRootDistance:
              maxRootDistance = sourceCacheEntry.rootDistance

          if cacheEntry is None:
            cacheEntry = CacheEntry(isRoot = False, isHotnode = True, precedesHotnode = False, rootDistance = maxRootDistance + 1)
            self._committed[node] = cacheEntry
          else:
            cacheEntry.isRoot = False
            cacheEntry.isHotnode = (cacheEntry.age > 1) # True iff the node was not in the previous graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = maxRootDistance + 1
            cacheEntry.age = 0

        node.cacheEntry = cacheEntry
        return cacheEntry
    for leaf in graph.leaves:
      traverse(leaf)

    # Replace the priority queue
    self._priorityQueue = PriorityQueue(self._committed)

    # Debug
    self.visualisePriorities(graph, "D:\\Desktop\\priorities.png")



  def visualisePriorities(self, graph, filepath):
    import pydotplus

    G = pydotplus.Dot(graph_type = "digraph")

    visited = {}
    def traverse(node, pydotSuccessor):
      if node in visited:
        pydotNode = visited[node]
        G.add_edge(pydotplus.Edge(pydotNode, pydotSuccessor))
      else:
        if node.cacheEntry.isHotnode:
          fillColour = "#ff5555"
        elif node.cacheEntry.precedesHotnode:
          fillColour = "#8888ff"
        else:
          fillColour = "#ffffff"
        keyNode = None
        for potentialKey in self._committed:
          if potentialKey == node:
            keyNode = potentialKey
            break
        pydotNode = pydotplus.Node("{}\np={}\nn={}".format(keyNode, round(self._committed[keyNode].priority, 1), len(self._committed[keyNode])), style = "filled", fillcolor = fillColour)
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
        G.add_node(pydotplus.Node("{}, {}".format(node, round(node.cacheEntry.priority, 1)), style = "filled", fillcolor = "#aaaaaa"))

    G.write_png(filepath)



# Initialise an empty cache
currentCache = Cache(maxSize = 100 * 1024 * 1024) # 100 MiB



class CacheEntry(dict):
  """CacheEntry()

  Represents the cached data of a single clip. Also contains properties representing the clip's
  priority, and whether or not it is new to the cache.
  """



  def __init__(self, isRoot, isHotnode, precedesHotnode, rootDistance):
    super().__init__()

    self.age = 0
    self.isRoot = isRoot
    self.isHotnode = isHotnode
    self.precedesHotnode = precedesHotnode
    self.rootDistance = rootDistance



  def discardBytes(self, target):
    """discardBytes(target)

    Discard at least `target` bytes of data from this cache entry, and return the exact number
    of bytes discarded.
    """

    bytesToDiscard = 0
    victims = []
    for n, data in self.items():
      victims.append(n)
      bytesToDiscard += data.nbytes
      if bytesToDiscard > target:
        break
    for victim in victims:
      del self[victim]

    return bytesToDiscard



  @property
  def priority(self):
    if self.precedesHotnode and not self.isHotnode:
      return (self.rootDistance + 100.0) / (2**self.age)
    else:
      return self.rootDistance / (2**self.age)



class PriorityQueue(object):
  """PriorityQueue()

  Keeps track of clips in the cache in ascending order of their priority.
  """



  def __init__(self, cache):
    self._cacheEntries = sorted(cache.values(), key = lambda entry: entry.priority)

    # Find the index of the lowest-priority nonempty cache entry
    self._victimIndex = None
    self.findNewVictim(start = 0)



  def peek(self):
    if self._victimIndex is not None:
      return self._cacheEntries[self._victimIndex]
    else:
      return None



  def findNewVictim(self, start = None):
    # Find the index of the lowest-priority nonempty cache entry
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

