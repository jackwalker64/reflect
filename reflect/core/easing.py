# -*- coding: utf-8 -*-

# All of these easing functions take the following parameters:
#   t: current time
#   b: start value
#   c: total change in value
#   d: duration

def linear(t, b, c, d):
  return c*t/d + b

def inQuad(t, b, c, d):
  t /= d
  return c*t*t + b

def outQuad(t, b, c, d):
  t /= d
  return -c * t*(t-2) + b

def inOutQuad(t, b, c, d):
  t /= d/2
  if t < 1:
    return c/2*t*t + b
  else:
    t -= 1
    return -c/2 * (t*(t-2) - 1) + b

def inCubic(t, b, c, d):
  t /= d
  return c*t*t*t + b

def outCubic(t, b, c, d):
  t /= d
  t -= 1
  return c*(t*t*t + 1) + b

def inOutCubic(t, b, c, d):
  t /= d/2
  if t < 1:
    return c/2*t*t*t + b
  else:
    t -= 2
    return c/2*(t*t*t + 2) + b

def inQuart(t, b, c, d):
  t /= d
  return c*t*t*t*t + b

def outQuart(t, b, c, d):
  t /= d
  t -= 1
  return -c * (t*t*t*t - 1) + b

def inOutQuart(t, b, c, d):
  t /= d/2
  if t < 1:
    return c/2*t*t*t*t + b
  else:
    t -= 2
    return -c/2 * (t*t*t*t - 2) + b

def inQuint(t, b, c, d):
  t /= d
  return c*t*t*t*t*t + b

def outQuint(t, b, c, d):
  t /= d
  t -= 1
  return c*(t*t*t*t*t + 1) + b

def inOutQuint(t, b, c, d):
  t /= d/2
  if t < 1:
    return c/2*t*t*t*t*t + b
  else:
    t -= 2
    return c/2*(t*t*t*t*t + 2) + b

def inSine(t, b, c, d):
  import math
  return -c * math.cos(t/d * (math.pi/2)) + c + b

def outSine(t, b, c, d):
  import math
  return c * math.sin(t/d * (math.pi/2)) + b

def inOutSine(t, b, c, d):
  import math
  return -c/2 * (math.cos(math.pi*t/d) - 1) + b

def inExpo(t, b, c, d):
  return c * pow( 2, 10 * (t/d - 1) ) + b

def outExpo(t, b, c, d):
  return c * ( -pow( 2, -10 * t/d ) + 1 ) + b

def inOutExpo(t, b, c, d):
  t /= d/2
  if t < 1:
    return c/2 * pow( 2, 10 * (t - 1) ) + b
  else:
    t -= 1
    return c/2 * ( -pow( 2, -10 * t) + 2 ) + b

def inCirc(t, b, c, d):
  import math
  t /= d
  return -c * (math.sqrt(1 - t*t) - 1) + b

def outCirc(t, b, c, d):
  import math
  t /= d
  t -= 1
  return c * math.sqrt(1 - t*t) + b

def inOutCirc(t, b, c, d):
  import math
  t /= d/2
  if t < 1:
    return -c/2 * (math.sqrt(1 - t*t) - 1) + b
  else:
    t -= 2
    return c/2 * (math.sqrt(1 - t*t) + 1) + b
