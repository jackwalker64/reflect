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

    Sets the current global cache to `newCache`, and returns the old cache.
    """

    oldCache = globals()["currentCache"]
    globals()["currentCache"] = newCache
    return oldCache



  def __init__(self):
    # These two-level dicts implement functions (clip → n → data).
    # They are expected (but not strictly required) to be disjoint, i.e.
    #   (n in committed[clip]) <-> not(n in staged[clip]).
    self.committed = {} # Persistent store
    self.staged = {}    # Temporary staging area, emptied at the end of script execution



  def explicitChecker(f):
    varnames = f.__code__.co_varnames
    def wrapper(*a, **kw):
      kw["explicitParams"] = set(list(varnames[:len(a)]) + list(kw.keys()))
      return f(*a, **kw)
    return wrapper

  @explicitChecker
  def get(self, clip, n, default = None, explicitParams = None):
    # Check the staging area
    if clip in self.staged:
      if n in self.staged[clip]:
        return self.staged[clip][n]

    # Check the persistent store
    if clip in self.committed:
      if n in self.committed[clip]:
        return self.committed[clip][n]

    # The sought data is neither cached nor staged for caching.
    if "default" in explicitParams:
      return default
    else:
      raise KeyError((clip, n))



  def stage(self, clip, n, data):
    if clip in self.staged:
      self.staged[clip][n] = data
    else:
      self.staged[clip] = { n: data }



# Initialise an empty cache
currentCache = Cache()
