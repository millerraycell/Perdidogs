import socket
from _thread import *
import threading

def threads(c):
    while True:
        data = c.recv(4096)
        print(data)
        
        if not data:
            print("Not valid")
            break

        data = data[::-1]
        c.send(data)

    c.close()

host = ""
port = 3001
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print_lock = threading.Lock()

s.bind((host, port))

s.listen(5)

while True:
    c, address = s.accept()

    print("Connected with: ", address[0], ':', address[1])

    start_new_thread(threads, (c,))
