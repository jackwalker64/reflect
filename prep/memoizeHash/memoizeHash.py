
# def memoizeHash(f):
#   """@memoizeHash

#   A simple decorator for permanently caching the result __hash__.
#   """

#   def wrapper(o):
#     if o.myCachedHash == 1:
#       o.myCachedHash = f(o)
#     return o.myCachedHash

#   return wrapper



# class A(object):
#   def __init__(self):
#     self.myCachedHash = 1

#   @memoizeHash
#   def hhh(self):
#     print("Computing hash of {} which is of type {}".format(self, type(self)))
#     return 21

# # @memoizeHash
# # def hhh(x):
# #   print("Computing hash of {}".format(x))
# #   return 21

# a = A()
# b = A()
# print("a.hhh() == {}".format(a.hhh()))
# print("b.hhh() == {}".format(b.hhh()))
# print("a.hhh() == {}".format(a.hhh()))
# print("b.hhh() == {}".format(b.hhh()))



# def g(a, b, c):
#   print("summing")
#   return a + b + c
# x = memoizeHash(g)
# print(x(1, 2, 3))
# print(x(4, 5, 6))


