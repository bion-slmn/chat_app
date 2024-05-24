#!/usr/binenv python3
'''
Create a server to chat app
'''
import socket
import json
import threading
import logging


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

        # make the port reusable
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.listen(5)
        self.message_logger(
            f' Starting server at PORT {self.port} IP {self.ip_address}')

    def accept_connection(self):
        '''
        accept connection from the client
        '''
        return self.server.accept()

    def start_thread(self, client_socket, ip_address, port):
        '''
        for each clieent,  create a thread and handle the conmunication
        '''
        thread = threading.Thread(
            target=self.handle_client, args=(
                client_socket, ip_address))
        thread.start()

    def send_message(self, message):
        '''
        send a message to the receiver number
        '''
        try:
            reciever_number = message.get('to')
            receiver_socket = self.clients.get(reciever_number)

            if receiver_socket:
                data = {'from': reciever_number,
                        'message': message.get('text'),
                        }
                json_data = json.dumps(data)
                receiver_socket.send(json_data.encode('utf-8'))
                return True
            return False
        except Exception as error:
            del self.clients[reciever_number]
            message_logger(f'Error : {reciever_number} Not connected')

    def handle_client(self, client_socket, address):
        '''
        handle iformation from the client
        '''

        while True:
            message = client_socket.recv(1024).decode('utf-8')

            if not message:
                client_socket.close()
                break

            message = json.loads(message)

            # store the client
            client_number = message.get('from')
            self.clients[client_number] = client_socket
            sent = self.send_message(message)

            if not sent:
                client_socket.send(b'Phone number your sennt to no registered')

    def start_server(self):
        '''
        start the server
        '''
        self.create_server()
        connected = True

        while connected:
            try:
                # connect accept connection
                conn, address = self.accept_connection()
                self.message_logger(f'Connection from {address}')

                # start a thread for each connection
                self.start_thread(conn, *address)

            except Exception as error:
                self.message_logger('Client Error, clossed connection', 30)
                conn.close()

    @staticmethod
    def message_logger(message, level=20):
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.log(level, message)


if __name__ == '__main__':
    server = Server(8000, 'localhost')
    server.message_logger
    server.start_server()
