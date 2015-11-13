
print("Enter callee")
print("x? = {}".format("x" in globals()))
x = 21

def main():
  print("Main of callee")
  print("x? = {}".format("x" in globals()))
  globals()["x"] = 42



if __name__ == "__main__":
  main()

print("Exit callee")
