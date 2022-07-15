import socket
import threading
class User:
    def __init__(self, nick=None, username=None):
        self.nick = nick
        self.username = username
        

    def is_registered(self):
        if self.nick != None and self.username != None:
            return True
        
class Server:
    def __init__(self, name, port, address):
        self.name = name
        self.address = address
        self.port = port
        self.socket = socket
        self.channels = {}
        self.connected_users = {} # socket : User
        self.registered_users = {}# NICK : socket


    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        def start_listening():
            while True:
                self.socket.listen()
                user, user_address = self.socket.accept()
                self.connected_users[user] = User()
                handle_user(user, user_address)

        def handle_user(user, user_address):
            user_thread = threading.Thread(target = listening_thread, args=(user, user_address))
            user_thread.start()

        def listening_thread(user, user_address): #clean up the registration portion.
            while True:
                message = user.recv(1024).decode()
                message_list = message.split()
                if message:
                    print(f"Received message : {message}")

                    if self.connected_users[user].is_registered():

                        if message_list[0] == 'PM':
                            msgtarget = message_list[1]
                            msg = ' '.join(message_list[2:])
                            source = self.connected_users[user].nick
                            msg = source + ':' + msg
                            private_message(source = source, msgtarget=msgtarget, msg=msg)
                        elif message_list[0] == 'BROAD':
                            msg = ' '.join(message_list[1:])
                            broadcast(msg)
                        elif message_list[0] == 'JOIN':
                            if message_list[1] not in self.channels:
                                self.channels[message_list[1]] = [self.connected_users[user].nick]
                                print(self.channels[message_list[1]])
                            else:
                                self.channels[message_list[1]].append(self.connected_users[user].nick)
                                print(self.channels[message_list[1]])
                        elif message_list[0][0] == '#':
                            source = self.connected_users[user].nick
                            channel = message_list[0]
                            msg = ' '.join(message_list[1:])
                            msg = source + ':' + msg
                            channel_message(channel=channel, msg=msg)
                    #registration
                    elif message_list[0] != 'NICK' and message_list[0] != 'USER':
                        reply = 'You must register before you can use the chat'
                        user.send(reply.encode())
                    elif message_list[0] == 'NICK':
                        if self.connected_users[user].nick == None:
                            self.connected_users[user].nick = message[4:].strip()
                            if self.connected_users[user].is_registered():
                                reply = f':{self.name}: Successfully registered! Welcome to the chat {self.connected_users[user].nick}!'
                                self.registered_users[self.connected_users[user].nick] = user
                                user.send(reply.encode())
                    elif message[0:4] == 'USER':
                        if self.connected_users[user].username == None:
                            self.connected_users[user].username = message[4:].strip()
                            if self.connected_users[user].is_registered():
                                reply = f':{self.name}: Successfully registered! Welcome to the chat {self.connected_users[user].nick}!'
                                self.registered_users[self.connected_users[user].nick] = user
                                user.send(reply.encode())

                else:
                    return

        def broadcast(msg):
            for user in self.registered_users.keys():
                self.registered_users[user].send(msg.encode())

        def private_message(msgtarget, msg):
            self.registered_users[msgtarget].send(msg.encode())
        
        def channel_message(channel, msg):
            for nick in self.channels[channel]:
                self.registered_users[nick].send(msg.encode())

        start_listening()
        

my_server = Server('test_server', 8000,'0.0.0.0')
my_server.start()
