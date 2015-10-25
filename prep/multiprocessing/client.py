from multiprocessing.connection import Client
import time

address = ("localhost", 6000)
conn = Client(address, authkey="secret password".encode(encoding="UTF-8"))

print("... receiving", time.time())
print("len is " + str(len(conn.recv())))
print("... received", time.time())

conn.close()
