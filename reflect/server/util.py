class _Getch:
  """Gets a single character from standard input. Does not echo to the screen."""

  def __init__(self):
    try:
      self.impl = _GetchWindows()
    except ImportError:
      self.impl = _GetchUnix()

  def __call__(self): return self.impl()


class _GetchUnix:
  def __init__(self):
    import tty, sys

  def __call__(self):
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
    finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class _GetchWindows:
  def __init__(self):
    import msvcrt

  def __call__(self):
    import msvcrt
    return msvcrt.getch()

getch = _Getch()



def prompt(default = "", buttonText = "Submit"):
  import tkinter

  root = tkinter.Tk()
  e = tkinter.Entry(root)
  e.pack()
  e.insert(0, default)
  e.focus_set()

  response = None

  def callback():
    response = e.get()
    root.destroy()

  def setFocus():
    root.focus_force()
    e.focus_set()

  b = tkinter.Button(root, text = buttonText, command = callback)
  b.pack(side = tkinter.BOTTOM)

  root.after(500, setFocus)

  root.mainloop()

  return response
