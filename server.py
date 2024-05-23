#!/usr/binenv python3
'''
Create a server to chat app
'''
import socket
import json
import threading


class Server:
    '''
    Defines a server object for the chat app
    '''
    def __init__(self, port, ip_address):
        '''
        initialise the server
        '''
        self.port = port
        self.ip_address = ip_address
        self.server = ''
        self.clients = {}

    def create_server(self):
        '''
        create a server socket
        '''
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip_address, self.port))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)
        print(f' Starting server at PORT {self.port} IP {self.ip_address}')
    
    def accept_connection(self):
        '''
        accept connection from the client
        '''
        return self.server.accept()

    def start_thread(self, client_socket, ip_address, port):
        '''
        for each clieent,  create a thread and handle the conmunication
        '''
        thread = threading.Thread(target=self.handle_client, args=(client_socket, ip_address))
        thread.start()

    def handle_client(self, client_socket, address):
        '''
        handle iformation from the client
        '''
        message = client_socket.recv(1024).decode('utf-8')
        message = json.loads(message)
        print(f'Recieved message : { message}')


    def start_server(self):
        '''
        start the server 
        ''' 
        self.create_server()
        connected = True

        while connected:
            conn, address = self.accept_connection()
            self.start_thread(conn, *address)



server = Server(8000, 'localhost')
server.start_server()

    



    