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



  def __init__(self):
    # These two-level dicts implement functions (clip → n → data).
    # They are expected (but not strictly required) to be disjoint, i.e.
    #   (n in committed[clip]) -> not(n in staged[clip]),
    #   (n in staged[clip])    -> not(n in committed[clip]).
    self._committed = {} # Persistent store
    self._staged = {}    # Temporary staging area, emptied at the end of script execution

    self.userScriptIsRunning = False # Determines which store to send incoming frames to



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



  def set(self, clip, n, image):
    if self.userScriptIsRunning:
      self.stage(clip, n, image)
    else:
      print("figure out priority of {} and possibly store frame {}".format(clip, n))



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
    2. Hotnodes:      Boost priorities of predecessors of "new" cache entries

    Preconditions:
    * Every `clip` in `graph` must satisfy "clip.cacheEntry is None", i.e. this graph hasn't been
      used in a previous reprioritise call.

    Side effects:
    * Each clip in `graph` has a `cacheEntry` property pointing to its entry in the cache.
    """

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
            cacheEntry = CacheEntry()
            cacheEntry.isRoot = True
            cacheEntry.isHotnode = True
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = 0
            self._committed[node] = cacheEntry
            print("*** added a root entry for {}".format(node))
          else:
            cacheEntry.isRoot = True
            cacheEntry.isHotnode = False # TODO: what if it was dead but now added back to the graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = 0
        elif isinstance(node._source, tuple):
          cacheEntry = self._committed.get(node, None)

          # First visit this node's sources
          maxRootDistance = None
          for source in node._source:
            sourceCacheEntry = traverse(source)
            if cacheEntry is None:
              # This node is hot, so we need to update the entry of the predecessor
              sourceCacheEntry.precedesHotnode = True
            if maxRootDistance is None or sourceCacheEntry.rootDistance > maxRootDistance:
              maxRootDistance = sourceCacheEntry.rootDistance

          if cacheEntry is None:
            cacheEntry = CacheEntry()
            cacheEntry.isRoot = False
            cacheEntry.isHotnode = True
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = maxRootDistance + 1
            self._committed[node] = cacheEntry
            print("*** added an entry for {}".format(node))
          else:
            cacheEntry.isRoot = False
            cacheEntry.isHotnode = False # TODO: what if it was dead but now added back to the graph
            cacheEntry.precedesHotnode = False
            cacheEntry.rootDistance = maxRootDistance + 1

        # print("Visiting {} (isRoot = {}, rootDistance = {}, isHotnode = {}, precedesHotnode = {}, priority = {})".format(node, cacheEntry.isRoot, cacheEntry.rootDistance, cacheEntry.isHotnode, cacheEntry.precedesHotnode, cacheEntry.priority))
        node.cacheEntry = cacheEntry
        return cacheEntry

    for leaf in graph.leaves:
      traverse(leaf)

    for node, entry in self._committed.items():
      print("entry for {}: (isRoot = {}, rootDistance = {}, isHotnode = {}, precedesHotnode = {}, priority = {})".format(node, entry.isRoot, entry.rootDistance, entry.isHotnode, entry.precedesHotnode, entry.priority))




# Initialise an empty cache
currentCache = Cache()



class CacheEntry(dict):
  """CacheEntry()

  Represents the cached data of a single clip. Also contains properties representing the clip's
  priority, and whether or not it is new to the cache.
  """



  def __init__(self):
    super().__init__()

    self.isRoot = None
    self.isHotnode = None
    self.precedesHotnode = None
    self.rootDistance = None



  @property
  def priority(self):
    if self.precedesHotnode and not self.isHotnode:
      return self.rootDistance + 100
    else:
      return self.rootDistance
