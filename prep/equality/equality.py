
class A1:
  def __init__(self, a1):
    self.a1 = a1

  def __eq__(self, other):
    return isinstance(other, A1) and self.a1 == other.a1

class A2:
  def __init__(self, a2):
    self.a2 = a2

  def __eq__(self, other):
    return isinstance(other, A2) and self.a2 == other.a2

class B(A1):
  def __init__(self, a1, a2):
    super().__init__(a1)
    self.oth = a2

  def __eq__(self, other):
    print("test1")
    if isinstance(self, B):
      print("test2")
      if super(B, self).__eq__(other):
        print("test3")
        if self.oth == other.oth:
          print("ok")
          return True
    return False
    # return isinstance(self, B) and super(B, self).__eq__(super(B, other)) and self.oth == other.oth

x = A1(30)
y = A1(30)
print(x == y)

x = B(20, A2(21))
y = B(20, A2(22))
print(x == y)
y.oth.a2 = 21
print(x == y)
