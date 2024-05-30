import socket
import json
import threading
import logging
import sys
import signal


class Client:
    def __init__(self, port, ip_address):
        self.port = port
        self.ip_address = ip_address
        self.server = ''
        self.running = True

    def __enter__(self):
        '''
        start the server
        '''
        self.start_client()

    def __exit__(self, exc_type:str, exc_value: int, traceback: int) -> bool:
        '''
        exit well
        '''
        self.server.close()


    def create_server(self):
        try:
            # connect to the server
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.ip_address, self.port))
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.message_logger(
                f'Starting server at PORT {self.port} IP {self.ip_address}')
        except Exception as e:
            self.message_logger(f'Error occurred: {e}')
            sys.exit()

    def handle_client(self):
        while True:
            try:
                msg = self.server.recv(1024).decode('utf-8')
                if not msg:
                    self.server.close()
                self.message_logger(msg)
                print()
            except Exception as error:
                self.message_logger(f'Error: {error}', 30)
                self.server.close()
                break

    def start_client(self):
        phone_no = input('Enter Your Phone No: ')
        send_to = input('Enter the phone number of reciever :')

        self.create_server()

        # Start the client handler in a separate thread
        client_handler_thread = threading.Thread(target=self.handle_client)
        client_handler_thread.start()

        
        while self.running:
            try:
                msg = input('Enter message :')
                data = {'from': phone_no, 'text': msg, 'to': send_to}
                json_data = json.dumps(data)
                self.server.send(json_data.encode('utf-8'))
            except Exception as error:
                break

    @staticmethod
    def message_logger(message, level=20):
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.log(level, message)


with Client(8001, 'localhost'):
    print('Client clossed')

