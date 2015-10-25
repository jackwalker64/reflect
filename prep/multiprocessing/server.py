from multiprocessing.connection import Listener
import time

a = [42] * (1280*720*4*24) # 1 second of rgba 1280x720 at 24 fps
address = ("localhost", 6000)
listener = Listener(address, authkey="secret password".encode(encoding="UTF-8"))

print("waiting for connection")
conn = listener.accept()
print("connection accepted from", listener.last_accepted)

print("... sending", time.time())
conn.send(a)
print("... sent", time.time())

conn.close()
listener.close()
