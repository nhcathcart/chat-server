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
        self.connected_servers = []


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
                    try:
                        command = message_list[0]
                    except IndexError:
                        user.send('Cannot send empty messages/commands. Try again'.encode())
                    
                    if self.connected_users[user].is_registered():

                        if command == 'PM':
                            try:
                                msgtarget = message_list[1]
                                msg = ' '.join(message_list[2:])
                                source = self.connected_users[user].nick
                                msg = source + ':' + msg
                                private_message(msgtarget=msgtarget, msg=msg)
                            except IndexError:
                                user.send("Private messages must be in this format: PM <receipient's nickname> <message>".encode())
                            except KeyError:
                                user.send("That nickname could not be found. Try again".encode())

                        elif command == 'BROAD':
                            try:
                                msg = ' '.join(message_list[1:])
                                broadcast(msg)
                            except IndexError:
                                user.send("Broadcast messages must be in this format: BROAD <message>".encode())

                        elif command == 'JOIN':
                            try:
                                if message_list[1] not in self.channels:
                                    self.channels[message_list[1]] = [self.connected_users[user].nick]
                                    user.send(f":{self.name}: {message_list[1]} has been created.".encode())
                                    print(self.channels[message_list[1]])
                                else:
                                    source = self.connected_users[user].nick
                                    channel = message_list[1]
                                    msg = f':{self.name}:{source} has joined {channel}'
                                    self.channels[message_list[1]].append(self.connected_users[user].nick)
                                    channel_message(channel=channel, msg=msg)
                                    print(self.channels[message_list[1]])
                            except IndexError:
                                user.send("Join commands must be in this format: Join <#channel_name>".encode())

                        elif command[0] == '#':
                            try:
                                source = self.connected_users[user].nick
                                channel = command
                                msg = ' '.join(message_list[1:])
                                msg = source + ':' + msg
                                channel_message(channel=channel, msg=msg)
                            except IndexError:
                                user.send("Messages to a channel must be in this format: #<channel_name> <message>".encode())
                            except KeyError:
                                user.send("That channel doesn't exist. Try again or create it with: JOIN #<new_channel_name>".encode())
                        elif command == 'QUIT':
                            user_quit(user)
                            print(self.registered_users.keys())
                            print(self.connected_users.keys())
                            return
                        else:
                            user.send('Command not found'.encode())
                    #registration
                    elif command != 'NICK' and command != 'USER':
                        reply = 'You must register before you can use the chat'
                        user.send(reply.encode())
                    elif command == 'NICK':
                        new_nick = ''.join(message_list[1:])
                        if new_nick not in self.registered_users:
                            self.connected_users[user].nick = new_nick
                            if self.connected_users[user].is_registered():
                                reply = f':{self.name}: Successfully registered! Welcome to the chat {self.connected_users[user].nick}!'
                                self.registered_users[self.connected_users[user].nick] = user
                                user.send(reply.encode())
                                
                        else:
                            user.send('That Nickname is already taken. Try again.'.encode())
                    elif command == 'USER':
                        if self.connected_users[user].username == None:
                            self.connected_users[user].username = ''.join(message_list[1:])
                            if self.connected_users[user].is_registered():
                                reply = f':{self.name}: Successfully registered! Welcome to the chat {self.connected_users[user].nick}!'
                                self.registered_users[self.connected_users[user].nick] = user
                                user.send(reply.encode())
                    
                else:
                    user_quit(user)
                    print(self.registered_users.keys())
                    print(self.connected_users.keys())
                    return

        def broadcast(msg):
            for user in self.registered_users.keys():
                self.registered_users[user].send(msg.encode())

        def private_message(msgtarget, msg):
            self.registered_users[msgtarget].send(msg.encode())
        
        def channel_message(channel, msg):
            for nick in self.channels[channel]:
                self.registered_users[nick].send(msg.encode())
        def user_quit(user):
            user.send('You have disconnected from the server.'.encode())
            try:
                del self.registered_users[self.connected_users[user].nick]
            except KeyError:
                pass
            try:
                del self.connected_users[user]
            except KeyError:
                pass
        start_listening()
        
server_name = 'chat-server'
port = 8000
address = '0.0.0.0'
my_server = Server(server_name, port, address)
print(f"{server_name} is now running.")
my_server.start()
