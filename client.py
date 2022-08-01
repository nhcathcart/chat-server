#client.py
import socket
import threading
test='test'

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost" # "127.0.1.1"
port = 8000
my_socket.connect((host, port))
def thread_sending():
    while True:
        message_to_send = input()
        if message_to_send:
            my_socket.send(message_to_send.encode())
        
def thread_receiving():
    while True:
        message = my_socket.recv(1024).decode()
        print(message)
        
thread_send = threading.Thread(target=thread_sending)
thread_receive = threading.Thread(target=thread_receiving)
thread_send.start()
thread_receive.start()