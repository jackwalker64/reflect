
print("Enter caller")
x = 10

def main():
  x = 100
  print("Main of caller: calling callee")
  with open("./callee.py") as f:
    z = { "__name__": "__main__" }
    exec(f.read(), z)
  print("Finished calling callee")
  print("x = {}".format(x))
  print("x = {}".format(globals()["x"]))
  print(z["x"])



if __name__ == "__main__":
  main()

print("Exit caller")

# experiment conclusion:
# use exec(f.read(), z), where z is a dict that
# will be used as the callee's global variables
# and should therefore initially contain
# "__name__": "__main__"

