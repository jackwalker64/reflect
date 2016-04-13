import unittest
import reflect
import logging
import sys
import numpy
import random
import pygame
import cv2

pygame.init()
random.seed(42)

bbb_480p_avi_path = "D:/Documents/University/Year 3/_Project/Media/sources/bbb_480p.avi"



def reflect_session(test_func):
  def do_test(self, *args, **kwargs):
    import warnings
    warnings.simplefilter("ignore") # Allow ffmpeg readers to persist

    reflect.setMode("server")
    reflect.setTransformations(["CanonicalOrder", "FlattenConcats"])
    reflect.cache.Cache.current().swap(reflect.cache.SpecialisedCache(100*1024*1024)) # Reset the cache
    reflect.CompositionGraph.reset()

    test_func(self, *args, **kwargs)

    for filepath, readers in reflect.core.roots.load.openReaders.items():
      for reader in readers:
        reader.close()
    reflect.core.roots.load.openReaders = {}

  return do_test



class CacheTestCase(unittest.TestCase):

  def test_swapping(self):
    c = reflect.cache.Cache.current()
    assert(c == c)
    c.swap(reflect.cache.SpecialisedCache(10))
    c2 = reflect.cache.Cache.current()
    assert(c != c2)
    c2.swap(c)
    assert(c == reflect.cache.Cache.current())
    c2.swap(c2)
    assert(c2 == reflect.cache.Cache.current())



  def test_locking_staging_area(self):
    c = reflect.cache.Cache.current()

    c.lockStagingArea()

    caughtException = False
    try:
      c.lockStagingArea()
    except:
      caughtException = True
    assert(caughtException)

    c.unlockStagingArea()

    caughtException = False
    try:
      c.unlockStagingArea()
    except:
      caughtException = True
    assert(caughtException)



  @reflect_session
  def test_get_set(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.load(bbb_480p_avi_path)
    y = x.blur(5)
    z = x.concat(y)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    images = [(n, x.frame(n)) for n in [0, int(x.frameCount / 2), x.frameCount - 1]]
    for n, image in images:
      assert(numpy.array_equal(image, cache.get(x, n)))



  @reflect_session
  def test_staging_result(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.load(bbb_480p_avi_path)
    y = x.blur(5)
    z = x.concat(y)
    yImage = y.frame(y.frameCount - 1)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    self.assertTrue(numpy.array_equal(yImage, cache.get(y, y.frameCount - 1)))



  @reflect_session
  def test_caching_indirections(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.load(bbb_480p_avi_path)
    y = x.blur(5)
    z = x.concat(y)
    zImage = z.frame(0)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    with self.assertRaises(KeyError) as cm:
      cache.get(z, 0) # z is an indirection so its frames shouldn't be cached



  @reflect_session
  def test_cache_entries(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.load(bbb_480p_avi_path)
    y = x.blur(5)
    z = x.concat(y)
    cache.userScriptIsRunning = False

    assert(x.cacheEntry is None)
    assert(y.cacheEntry is None)
    assert(z.cacheEntry is None)

    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    assert(x.cacheEntry is not None)
    assert(y.cacheEntry is not None)
    assert(z.cacheEntry is not None)



class EasingFunctionTestCase(unittest.TestCase):

  def test_defaults(self):
    from reflect.core.easing import linear, inQuad, outQuad, inOutQuad, inCubic, outCubic, inOutCubic, inQuart, outQuart, inOutQuart, inQuint, outQuint, inOutQuint, inSine, outSine, inOutSine, inExpo, outExpo, inOutExpo, inCirc, outCirc, inOutCirc
    fs = [linear, inQuad, outQuad, inOutQuad, inCubic, outCubic, inOutCubic, inQuart, outQuart, inOutQuart, inQuint, outQuint, inOutQuint, inSine, outSine, inOutSine, inExpo, outExpo, inOutExpo, inCirc, outCirc, inOutCirc]

    start = 50
    delta = 100
    duration = 10
    for f in fs:
      for t in range(duration):
        assert(start <= f(t, start, delta, duration) <= start + delta)



class GraphTestCase(unittest.TestCase):

  def test_graph_swapping(self):
    reflect.CompositionGraph.reset()

    def nodegen():
      return reflect.load(bbb_480p_avi_path)

    g = reflect.CompositionGraph.current()
    self.assertTrue(len(g.leaves) == 0)
    n = nodegen()
    self.assertTrue(g.isLeaf(n))
    self.assertTrue(len(g.leaves) == 1)
    g.removeLeaf(nodegen())
    self.assertTrue(len(g.leaves) == 0)
    self.assertTrue(not g.isLeaf(n))
    self.assertTrue(g.isLeaf(nodegen()))
    self.assertTrue(g.isLeaf(n))



class TimecodesTestCase(unittest.TestCase):

  def test_timecodes(self):
    ns = [-100, 0, 100, 200, 300, 400, 500, 600, 700, 800, 900]
    ts = ["-00:00:03.33", "00:00:00.00", "00:00:03.33", "00:00:06.67", "00:00:10.00", "00:00:13.33", "00:00:16.67", "00:00:20.00", "00:00:23.33", "00:00:26.67", "00:00:30.00"]
    fps = 30

    for n, t in zip(ns, ts):
      self.assertEqual(reflect.core.util.frameToTimecode(n, fps), t)
      self.assertEqual(reflect.core.util.timecodeToFrame(t, fps), n)

    fps = 30
    ts = ["1", "1.5", "0.5:3"]
    ns = [30, 45, (0.5*60+3)*fps]

    for n, t in zip(ns, ts):
      self.assertEqual(reflect.core.util.timecodeToFrame(t, fps), n)



  def test_subclip_parameters(self):
    interpretSubclipParameters = reflect.core.util.interpretSubclipParameters

    passes = [
      (0, 100, 0, 100),
      (10, 90, 10, 90),
      (-20, 90, 80, 90),
      (-30, -20, 70, 80),
      (-30, -1, 70, 99)
    ]

    for n1, n2, outN1, outN2 in passes:
      self.assertEqual(interpretSubclipParameters(n1, n2, frameCount = 100), (outN1, outN2))

    fails = [
      (-20, 10),
      (80, 10),
      (30, 0),
      (-30, 0)
    ]

    for n1, n2 in fails:
      with self.assertRaises(ValueError) as cm:
        _ = interpretSubclipParameters(n1, n2, frameCount = 100)



class ClipsTestCase(unittest.TestCase):

  def test_memoisation(self):
    memoizeHash = reflect.core.clips.memoizeHash

    callsToF = [0]
    callsToG = [0]

    class A(object):
      def f(self):
        callsToF[0] += 1
        return "f's result"

      @memoizeHash
      def g(self):
        callsToG[0] += 1
        return "g's result"

    a = A()

    self.assertEqual(a.f(), "f's result")
    self.assertEqual(a.g(), "g's result")
    self.assertEqual(a.f(), "f's result")
    self.assertEqual(a.g(), "g's result")
    self.assertEqual(callsToF[0], 2)
    self.assertEqual(callsToG[0], 1)



  @reflect_session
  def test_metadata(self):
    m = reflect.core.clips.VideoClipMetadata(size = (1920, 1080), frameCount = 100, fps = 30)

    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.core.clips.VideoClip("source", m)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    self.assertEqual(x.size, (1920, 1080))
    self.assertEqual(x.duration, 100 / 30)
    self.assertEqual(x.fps, 30)
    self.assertEqual(x.width, 1920)
    self.assertEqual(x.height, 1080)
    self.assertEqual(x.aspectRatio, (16, 9))
    self.assertEqual(x.frameCount, 100)



  @reflect_session
  def test_equality(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x = reflect.load(bbb_480p_avi_path)
    y = x.blur(5)
    Y = x.blur(5)
    z = x.concat(y)
    Z = y.concat(x)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True
    x2 = reflect.load(bbb_480p_avi_path.replace("/", "\\"))
    y2 = x2.blur((5, 5))
    z2 = x2.concat(y2)
    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()

    self.assertEqual(x, x)
    self.assertEqual(y, y)
    self.assertEqual(y, Y)
    self.assertEqual(z, z)
    self.assertNotEqual(z, Z)

    self.assertEqual(x2, x2)
    self.assertEqual(y2, y2)
    self.assertEqual(z2, z2)

    self.assertEqual(x, x2)
    self.assertEqual(y, y2)
    self.assertEqual(z, z2)



  @reflect_session
  def test_concat_flattening(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y = x.concat(x).concat(x).concat(x)
    z = x.concat(x, x, x)
    reflect.CompositionGraph.current().flattenConcats()

    leaves = reflect.CompositionGraph.current().leaves
    for leaf in leaves:
      break
    self.assertEqual(len(leaves), 1)
    self.assertEqual(leaf, z)
    reflect.CompositionGraph.current().removeLeaf(z)

    x = reflect.load(bbb_480p_avi_path)
    y = x.concat(x).concat(x).concat(x)
    z = x.concat(x, x, x)

    leaves = reflect.CompositionGraph.current().leaves
    for leaf in leaves:
      break
    self.assertEqual(len(leaves), 2)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_load(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    self.assertEqual(x.size, (854, 480))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_text(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.text("hello world", font = "arial", size = 12, bold = True)
    with self.assertRaises(Exception) as cm:
      x = reflect.text("hello world", font = "D:/NonExistentFont.ttf", size = 12, bold = True)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_blur(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y1 = x.blur(5)
    y2 = x.blur((5, 5))
    y3 = x.blur(width = 5, height = 5)
    self.assertEqual(y1, y2)
    self.assertEqual(y2, y3)
    with self.assertRaises(Exception) as cm:
      y = x.blur((5, 5, 5))
    with self.assertRaises(Exception) as cm:
      y = x.blur()
    with self.assertRaises(Exception) as cm:
      y = x.blur(0)
    with self.assertRaises(Exception) as cm:
      y = x.blur((-3, 3))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_brighten(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    self.assertEqual(x.brighten(0.3).brighten(0.3), x.brighten(0.51))
    y = x.brighten(-1)
    y = x.brighten(0)
    y = x.brighten(0.5)
    y = x.brighten(1)
    with self.assertRaises(Exception) as cm:
      y = x.brighten(1.01)
    with self.assertRaises(Exception) as cm:
      y = x.brighten(-1.01)
    with self.assertRaises(Exception) as cm:
      y = x.brighten(float("inf"))
    with self.assertRaises(Exception) as cm:
      y = x.brighten(float("-inf"))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_composite(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    reflect.setTransformations([])
    x = reflect.load(bbb_480p_avi_path)
    y = x.resize(width = 200, height = 200)
    z = x.resize(width = 100, height = 100)

    a = y.composite(z, x1 = 100, y1 = 100)
    b = y.composite(z, x1 = 199, y1 = 100)
    c = y.composite(z, x1 = 100, y1 = 199)
    self.assertEqual(type(a), reflect.vfx.composite.CompositeVideoClip)
    self.assertEqual(type(b), reflect.vfx.composite.CompositeVideoClip)
    self.assertEqual(type(c), reflect.vfx.composite.CompositeVideoClip)

    d = y.composite(z, x1 = 200, y1 = 100)
    e = y.composite(z, x1 = 100, y1 = 200)
    f = y.composite(z, x1 = -100, y1 = 100)
    g = y.composite(z, x1 = 100, y1 = -100)
    self.assertNotEqual(type(d), reflect.vfx.composite.CompositeVideoClip)
    self.assertNotEqual(type(e), reflect.vfx.composite.CompositeVideoClip)
    self.assertNotEqual(type(f), reflect.vfx.composite.CompositeVideoClip)
    self.assertNotEqual(type(g), reflect.vfx.composite.CompositeVideoClip)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_crop(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y = x.resize(width = 200, height = 200)

    a = y.crop(x1 = 100, y1 = 100, width = 50, height = 50)
    b = y.crop(x1 = 150, y1 = 100, width = 50, height = 50)
    c = y.crop(x1 = 100, y1 = 150, width = 50, height = 50)

    with self.assertRaises(Exception) as cm:
      d = y.crop(x1 = 151, y1 = 100, width = 50, height = 50)
    with self.assertRaises(Exception) as cm:
      e = y.crop(x1 = 100, y1 = 151, width = 50, height = 50)
    with self.assertRaises(Exception) as cm:
      f = y.crop(x1 = -1, y1 = 100, width = 50, height = 50)
    with self.assertRaises(Exception) as cm:
      g = y.crop(x1 = 100, y1 = -1, width = 50, height = 50)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_gaussianBlur(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y1 = x.gaussianBlur(5)
    y2 = x.gaussianBlur((5, 5))
    y3 = x.gaussianBlur(width = 5, height = 5)
    self.assertEqual(y1, y2)
    self.assertEqual(y2, y3)
    y3 = x.gaussianBlur(5, sigma = (5, 5))
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(5, sigma = "invalid")
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(5, sigma = -1)
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(5, sigma = float("inf"))
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(5, sigma = (1, -1))
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(5, sigma = (-1, 1))
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(0)
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(1.5)
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur(4)
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur((4, 4))
    with self.assertRaises(Exception) as cm:
      y = x.gaussianBlur((-3, 3))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_rate(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y = x.rate(fps = 30)
    z = x.rate(delay = 1/30)
    self.assertEqual(y, z)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_resize(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y1 = x.resize(width = 1280)
    y2 = x.resize(height = 1280/x.width*x.height)
    y3 = x.resize(size = 1280/x.width)
    self.assertEqual(y1, y2)

    z1 = x.resize(width = 100, interpolation = cv2.INTER_AREA)
    z2 = z1.resize(width = 100, interpolation = cv2.INTER_AREA)
    self.assertEqual(z1, z2)
    z3 = x.resize(width = 100, interpolation = cv2.INTER_NEAREST)
    self.assertNotEqual(z2, z3)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_reverse(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    self.assertEqual(x.reverse().reverse(), x)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_slide(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    f = reflect.core.easing.inOutQuad

    # f and g have different source code but perform the same function
    def g(t, b, c, d):
      return f(t, b, c, d)

    # h is a different function to f and g, but is equal within the transition domain
    def h(t, b, c, d):
      if t < 0 or t > d:
        return float("inf")
      else:
        return f(t, b, c, d)

    x = reflect.load(bbb_480p_avi_path)
    y1 = x.slide(x, "top", frameCount = 5, f = f)
    y2 = x.slide(x, "top", frameCount = 5, f = g)
    y3 = x.slide(x, "top", frameCount = 5, f = h)
    z = x.slide(x, "top", frameCount = 5, f = reflect.core.easing.inCubic)
    self.assertEqual(y1, y2)
    self.assertEqual(y2, y3)
    self.assertNotEqual(y1, z)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_speed(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path)
    y1 = x.speed(scale = 1/3)
    y2 = x.speed(frameCount = x.frameCount * 3)
    y3 = x.speed(duration = reflect.core.util.frameToTimecode(x.frameCount * 3, x.fps))
    self.assertEqual(y1, y2)
    self.assertEqual(y2, y3)

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_api_subclip(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    x = reflect.load(bbb_480p_avi_path).speed(frameCount = 50)
    y = x.concat(x)
    self.assertEqual(x.subclip(10, 20), y.subclip(10, 20))
    self.assertEqual(x.subclip(40).concat(x.subclip(frameCount = 10)), y.subclip(40, 60))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()



  @reflect_session
  def test_canonical_order(self):
    cache = reflect.cache.Cache.current()
    cache.userScriptIsRunning = True

    f1 = lambda x: x.crop(x1 = x.width / 4, x2 = x.width / 4 * 3, y1 = x.height / 4, y2 = x.height / 4 * 3)
    f2 = lambda x: x.resize(0.5)
    f3 = lambda x: x.brighten(0.3)
    f4 = lambda x: x.greyscale()
    f5 = lambda x: x.blur(width = 5, height = 3)
    f6 = lambda x: x.gaussianBlur(width = 13, height = 5, sigma = (2, 3))
    f7 = lambda x: x.rate(fps = x.fps*2)
    f8 = lambda x: x.reverse()
    f9 = lambda x: x.speed(2)
    f10 = lambda x: x.subclip(x.frameCount / 4, x.frameCount / 4 * 3)
    f11 = lambda x: x.resize(1.5)

    fs = [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11]

    x = reflect.load(bbb_480p_avi_path).speed(frameCount = 1000).resize((400, 400))

    import itertools
    import inspect

    for (f, g) in list(itertools.combinations_with_replacement(fs, 2)):
      skip = [(f1, f5), (f1, f6), (f5, f5), (f5, f6), (f5, f11), (f6, f6), (f6, f11), (f2, f11)]
      if (f, g) in skip or (g, f) in skip:
        # f(g(x)) and g(f(x)) are not expected to be equal, so skip the checks
        continue

      y = f(g(x))
      z = g(f(x))

      self.assertEqual(y.frameCount, z.frameCount, (inspect.getsource(f), inspect.getsource(g)))
      self.assertEqual(y.size, z.size, (inspect.getsource(f), inspect.getsource(g)))
      self.assertEqual(y, z, (inspect.getsource(f), inspect.getsource(g)))
      self.assertTrue(numpy.array_equal(y.frame(y.frameCount / 4), z.frame(y.frameCount / 4)), (inspect.getsource(f), inspect.getsource(g)))

    cache.userScriptIsRunning = False
    cache.reprioritise(reflect.CompositionGraph.current())
    cache.commit()












if __name__ == '__main__':
  logging.basicConfig(stream = sys.stderr, format = "%(levelname)s: %(message)s", level = logging.ERROR)

  unittest.main()
