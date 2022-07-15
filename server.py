#server.py
import socket
import threading

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 8000
ADDRESS = "0.0.0.0"

broadcast_list = []

my_socket.bind((ADDRESS, PORT))

def thread_accept():
    while True:
        my_socket.listen()
        client, client_address = my_socket.accept()
        broadcast_list.append(client)
        start_listenning_thread(client)

def start_listenning_thread(client):
    client_thread = threading.Thread(target = listen_thread, args=(client,))
    client_thread.start()

def listen_thread(client):
    while True:
        message = client.recv(1024).decode()
        if message:
            print(f"Received message : {message}")
            broadcast(message)
        else:
            return

def broadcast(message):
    for client in broadcast_list:
        client.send(message.encode())


thread_accept()