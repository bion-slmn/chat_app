#!/usr/binenv python3
'''
Create a server to chat app
'''
import socket
import json
import threading
import logging
import signal


class Server:
    '''
    Defines a server object for the chat app
    '''

    def __init__(self, port: int, ip_address: str) -> None:
        '''
        initialise the server
        '''
        self.port = port
        self.ip_address = ip_address
        self.server = ''
        self.clients = {}

    def __enter__(self) -> 'Server':
        '''
        start the server when the context manager useed
        '''
        self.message_logger(
            f'Start in server {self.port} and {self.ip_address}')
        self.start_server()
        return self

    def __exit__(self, exc_type: str, exc_value: int, traceback: int) -> bool:
        '''
        close the server on exiting
        '''
        if exc_type:
            self.message_logger(
                f"Exception {exc_type} occurred with value {exc_value}")
        # close clients
        for client in self.clients.values():
            client.close()

        self.server.close()
        self.message_logger('Sever has clossed')
        return True

    def sigInt_handler(self, signum: int, frame: type) -> None:
        '''
        handle the Ctr + C to exit
        '''
        self.connected = False
        self.server.close()

    def create_server(self) -> None:
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

    def accept_connection(self) -> None:
        '''
        accept connection from the client
        '''
        return self.server.accept()

    def start_thread(
            self,
            client_socket: socket,
            ip_address: str,
            port: int) -> None:
        '''
        for each clieent,  create a thread and handle the conmunication
        '''
        thread = threading.Thread(
            target=self.handle_client, args=(
                client_socket, ip_address))
        thread.start()

    def send_message(self, message: str):
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

    def handle_client(self, client_socket: socket, address: str):
        '''
        handle iformation from the client
        '''

        while self.connected:
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
        signal.signal(signal.SIGINT, self.sigInt_handler)
        self.create_server()
        self.connected = True

        while self.connected:
            try:
                conn, address = self.accept_connection()
                self.message_logger(f'Connection from {address}')

                # start a thread for each connection
                self.start_thread(conn, *address)

            except OSError as e:
                if not self.connected:
                    self.message_logger('Server is shutting down.')
                else:
                    self.message_logger(f'Error: {e}')
                break
            except Exception as error:
                conn.close()

    @staticmethod
    def message_logger(message, level=20):
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.log(level, message)


if __name__ == '__main__':
    with Server(8001, 'localhost'):
        print('start')
sys.exit()