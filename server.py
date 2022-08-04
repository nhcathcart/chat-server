import socket
import threading
import redis
import bcrypt

r = redis.Redis(host='localhost', port='6379', decode_responses=True)

class User:
    def __init__(self, nick=None, password=None):
        self.nick = nick
        self.password = password
        

    def is_registered(self):
        if self.nick != None and self.password != None:
            return True

class Server:
    def __init__(self, name, port, address):
        self.name = name
        self.address = address
        self.port = port
        self.socket = socket
        self.connected_users = {} # socket : User
        self.online_users = {} # NICK : socket


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
                    
                    try:
                        command = message_list[0]
                        print(f"Received message : {command}")
                    except IndexError:
                        user.send('Cannot send empty messages/commands. Try again'.encode())
                    
                    if self.connected_users[user].is_registered():
                        #commands for registered users
                        if command == 'PM':
                            pm(message_list, user)

                        elif command == 'BROAD':
                            broad(message_list, user)

                        elif command == 'WHOISONLINE':
                            who_is_online(message_list, user)

                        elif command == 'GETMEMBERS':
                            get_members(message_list, user)
                            
                        elif command == 'JOIN':
                            join(message_list, user)

                        elif command[0] == '#':
                            send_channel_message(message_list, user)

                        elif command == 'HELP':
                            help(user)

                        elif command == 'QUIT':
                            user_quit(user)
                            return

                        else:
                            user.send('Command not found'.encode())
                    #registration
                    elif command == 'LOGIN': 
                        login(message_list, user)

                    elif command == 'HELP':
                        help(user)

                    elif command != 'NICK' and command != 'PASS':
                        reply = 'You must register before you can use the chat'
                        user.send(reply.encode())

                    elif command == 'NICK':
                        set_nick(message_list, user)

                    elif command == 'PASS':
                        set_password(message_list, user)
                    
                else:
                    user_quit(user)
                    print(self.online_users.keys())
                    print(self.connected_users.keys())
                    return

        #command functions/registered users
        def pm(message_list, user):
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

        def broad(message_list, user):
            try:
                msg = ' '.join(message_list[1:])
                broadcast(msg)
            except IndexError:
                user.send("Broadcast messages must be in this format: BROAD <message>".encode())
        
        def who_is_online(message_list, user):
            for key in self.online_users.keys():
                msg = key + '\n'
                user.send(msg.encode())
        
        def get_members(message_list, user):
            channel = message_list[1]
            for nick in r.smembers(channel):
                msg = nick + '\n'
                user.send(msg.encode())

        def join(message_list, user):
            try:
                channel = ''.join(message_list[1:])
                if r.exists(channel) == 0:
                    r.sadd(channel, self.connected_users[user].nick)
                    user.send(f":{self.name}: {message_list[1]} has been created.".encode())
                else:
                    source = self.connected_users[user].nick
                    msg = f':{self.name}:{source} has joined {channel}'
                    r.sadd(channel, source)
                    members = r.smembers(channel)
                    channel_message(channel=channel, msg=msg, members=members)
            except IndexError:
                user.send("Join commands must be in this format: Join <#channel_name>".encode())
        def send_channel_message(message_list, user):
            try:
                channel = message_list[0]
                if r.exists(channel):
                    source = self.connected_users[user].nick
                    members = r.smembers(channel)
                    if source in members:
                        msg = ' '.join(message_list[1:])
                        msg = channel + ':'  + source + ': ' + msg
                        channel_message(channel=channel, msg=msg, members=members)
                    else:
                        user.send("You have not joined that channel. Use JOIN #<channel_name> to join the channel.".encode())
                else:
                    user.send("That channel could not be found. Try again or create it with the command JOIN #<channel_name>.".encode())
            except IndexError:
                user.send("Messages to a channel must be in this format: #<channel_name> <message>".encode())
            
        #command functions/registration
        def login(message_list, user):
            try:
                nick = message_list[1]
                password = message_list[2].encode()
                password_hash = r.hget(nick, 'password').encode()
                if bcrypt.checkpw(password, password_hash):
                    self.online_users[nick] = user
                    self.connected_users[user].nick = nick
                    self.connected_users[user].password = 'has_password'
                    user.send(f'Welcome back {message_list[1]}. Chat away.'.encode())
                else:
                    user.send('Incorrect password. Try again.'.encode())
            except IndexError:
                user.send('Login must be in this format. LOGIN <nickname> <password>'.encode())
            except AttributeError:
                user.send("Unable to find NICK. Try again.".encode())
        def set_nick(message_list, user):
            nick = ''.join(message_list[1:])
            if r.exists(nick) == 0:
                self.connected_users[user].nick = nick
                if self.connected_users[user].is_registered():
                    reply = f':{self.name}: You have successfully registered! Welcome to the chat {nick}!'
                    r.hset(self.connected_users[user].nick, 'password', self.connected_users[user].password)
                    self.online_users[nick] = user
                    user.send(reply.encode())        
            else:
                user.send('That Nickname is already taken. Try again.'.encode())
        def set_password(message_list, user):
            if self.connected_users[user].password == None:
                password = ''.join(message_list[1:]).encode()
                password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
                self.connected_users[user].password = password_hash
                if self.connected_users[user].is_registered():
                    nick = self.connected_users[user].nick
                    reply = f':{self.name}: You have successfully registered! Welcome to the chat {nick}!'
                    r.hset(self.connected_users[user].nick, 'password', self.connected_users[user].password)
                    self.online_users[self.connected_users[user].nick] = user
                    user.send(reply.encode())
        #command helper functions
        def broadcast(msg):
            for user in self.online_users.keys():
                self.online_users[user].send(msg.encode())
        def private_message(msgtarget, msg):
            self.online_users[msgtarget].send(msg.encode())
        
        def channel_message(channel, msg, members): 
            members = r.smembers(channel)
            for nick in self.online_users:
                if nick in members:
                    self.online_users[nick].send(msg.encode())

        def user_quit(user):
            user.send('You have disconnected from the server.'.encode())
            try:
                del self.online_users[self.connected_users[user].nick]
            except KeyError:
                pass
            try:
                del self.connected_users[user]
            except KeyError:
                pass
        #help
        def help(user):
            command_list = [
                'Login or register with a nickname and password to use the chat.\n', 
                'Action: How to format your command and message\n\n',
                '#####Registration#####\n\n',
                'Register Nickname: NICK <nickname>\n',
                'Register Password: PASS <password>\n',
                'Login with Nickname and Password: LOGIN <nickname> <password>\n\n',
                '#####Commands#####\n\n'
                'Private Message: PM <target_nick> <message>\n',
                'Broadcast: BROAD <message>\n',
                'Join Channel: JOIN #<channel_name>\n',
                'Send Channel Message: #<channel_name> <message>\n',
                'See Who is Online: WHOISONLINE\n',
                'Get list of channel subscribers: GETMEMBERS #<channel_name>\n',
                'HELP: HELP\n',
                'QUIT: QUIT'
            ]
            help_message = ''.join(command_list)
            user.send(help_message.encode())
        start_listening()
        
server_name = 'chat-server'
port = 8000
address = '0.0.0.0'
my_server = Server(server_name, port, address)
print(f"{server_name} is now running.")
my_server.start()