import socket
from _thread import *
import threading
import psutil

def thread_requisitor(host, port, m):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    soc.connect((host,port))

    soc.send(m.encode('ascii'))
    data = soc.recv(1024)

    print_lock.acquire()
    print("Reposta do Servidor\n", str(data.decode('ascii')), end="\n")
    print_lock.release()

    soc.close()

#host = "192.168.100.9"
host = "127.0.0.1"

port = 3001

print_lock = threading.Lock()

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# s.connect((host,port))

while True:
    # print_lock.acquire()
    mensagem = input("Mensagem para encaminhar para o servidor:\n")
    # print_lock.release()

    for i in [("Testando " + str(j)) for j in range(100)]:
        start_new_thread(thread_requisitor, (host, port, i,))

    """
    # s.send(mensagem.encode('ascii'))
    # data = s.recv(1024)

    # print("Reposta do Servidor\n", str(data.decode('ascii')))
    # print()
    """

    # gives a single float value
    #float x = psutil.cpu_percent()

    # print_lock.acquire()
    ans = input("Continuar (y/n)?\n")
    # print_lock.release()
    if (ans == 'y'):
        continue
    else:
        break

# s.close()
