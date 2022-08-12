# Chat Server

This is a basic chat server and client very loosely based on the IRC protocol. I made it to learn about socket programming. It registers users with a NICK(nickname) and a PASS(password). Users then can LOGIN to the server using their NICK and PASS in another session. It supports channels, private messaging, who is online, get channel members, and broadcast. It uses REDIS as a data store to persist nicknames, passwords, and channel subscribers.

To run this locally:

Clone the repository in the desired location on your machine.

Navigate to the cloned repository and run the following commands:

- ```docker network create <network_name>```
- ```docker build -t <server_name> .```     
- ```docker run --name myredis --network <network_name> -p 6379:6379 -d redis```
- ```docker run --name myserver --network <network_name> -p 8000:8000 <server_name>```

You can then interact with the server with Telnet or with the client included in the repo from another terminal window. Enter HELP for a command list.