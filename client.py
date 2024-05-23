import socket
import json
import threading


class Client:
    '''
    start Client
    '''
    def __init__(self, port, ip_address):
        '''
        initialise the server
        '''
        self.port = port
        self.ip_address = ip_address
        self.server = ''

    def create_server(self):
        '''
        create a server socket
        '''
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.ip_address, self.port))
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(f' Starting server at PORT {self.port} IP {self.ip_address}')
        except Exception as e:
            print(f'Error occured: {e}')

    
    def start_client(self):
        '''
        start the client
        '''
        self.create_server()
        data = {'from': '701036054'}
        json_data = json.dumps(data)
        self.server.send(json_data.encode('utf-8'))


client = Client(8000, 'localhost')
client.start_client()