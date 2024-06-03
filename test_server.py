
from unittest.mock import patch, MagicMock, call, PropertyMock
from server import Server
import unittest
import socket
import signal


class TestServer(unittest.TestCase):
    def setUp(self) -> None:
        '''
        run at the beginning of each test
        '''

        self.server = Server(8000, 'localhost')

    def test__init(self) -> None:
        '''
        test init function
        '''
        self.assertEqual(self.server.port, 8000)
        self.assertEqual(self.server.ip_address, 'localhost')
        self.assertEqual(self.server.server, '')
        self.assertEqual(self.server.clients, {})

    @patch('server.Server.__exit__', return_value=None)
    @patch('server.Server.message_logger')
    @patch('server.Server.start_server')
    def test__enter(self,
                    mock_start_server: MagicMock,
                    mock_message_logger: MagicMock,
                    mock_exit: MagicMock) -> None:
        '''
        test the enter method
        '''
        self.server = Server(8000, 'localhost')

        with Server(8000, 'localhost') as server:
            self.assertIsInstance(server, Server)
            message = 'Start in server 8000 and localhost'
            self.assertTrue(mock_message_logger.called)
            self.assertTrue(mock_start_server.called)
            mock_message_logger.assert_called_with(message)
            mock_message_logger.assert_called_once()
        mock_exit.assert_called()

    @patch('server.Server.message_logger')
    @patch('server.Server.start_server')
    def test__exit__(self,
                     mock_start_server: MagicMock,
                     mock_message_logger: MagicMock,) -> None:
        '''
        test the exit method without exception
        '''
        mock_close = MagicMock()
        self.server.server = mock_close
        mock_close.close.return_value = None
        with self.server:
            pass

        self.assertTrue(mock_message_logger.called)
        self.assertTrue(mock_close.close.called)
        mock_message_logger.assert_called_with('Sever has closed')
        self.assertEqual(mock_message_logger.call_count, 2)
        mock_message_logger.assert_has_calls(
            [
                call('Start in server 8000 and localhost'),
                call('Sever has closed')
            ])

    @patch('server.Server.message_logger')
    @patch('server.Server.start_server')
    def test__exit__with_Exception(self,
                                   mock_start_server: MagicMock,
                                   mock_message_logger: MagicMock,) -> None:
        '''
        test the exit method without exception
        '''
        mock_close = MagicMock()
        self.server.server = mock_close
        mock_close.close.return_value = None
        with self.server:
            raise valueError('Error has occured')

        self.assertTrue(mock_message_logger.called)
        self.assertTrue(mock_close.close.called)
        self.assertFalse(hasattr(self.server, '_suppress_exception'))
        mock_message_logger.assert_called_with('Sever has closed')
        self.assertEqual(mock_message_logger.call_count, 3)

    def test_signal(self) -> None:
        '''
        test the signal handler function
        '''
        mock_close = MagicMock()
        self.server.server = mock_close
        mock_close.close.return_value = None

        self.server.sigInt_handler(2, None)

        self.assertFalse(self.server.connected)
        mock_close.close.assert_called_once()

    @patch('server.socket.socket')
    @patch('server.Server.message_logger')
    def test_create_server(self,
                           mock_message_logger: MagicMock,
                           mock_socket: MagicMock) -> None:
        '''
         test create a server
        '''
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        self.server.create_server()

        mock_socket.assert_called_once_with(
            socket.AF_INET, socket.SOCK_STREAM
        )
        mock_socket_instance.bind.assert_called_once_with(('localhost', 8000))
        mock_socket_instance.setsockopt.assert_called_with(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_socket_instance.listen.assert_called_with(5)
        mock_message_logger.assert_called_once()
        mock_message_logger.assert_called_with(
            'Starting server at PORT 8000 IP localhost'
        )
        self.assertEqual(self.server.server, mock_socket_instance)

    def test_accept_connection(self) -> None:
        '''
        Test accept a connection
        '''
        mock_server = MagicMock()
        self.server.server = mock_server

        self.server.accept_connection()

        mock_server.accept.assert_called_once()
        mock_server.accept.assert_called_with()

    @patch('server.threading.Thread')
    def test_start_thread(self, mock_thread) -> None:
        '''
        test that a thread is started
        '''
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        client_socket = ''
        result = self.server.start_thread(
            client_socket, 'localhost', 5000
        )

        mock_thread.assert_called_once_with(
            target=self.server.handle_client, args=(
                client_socket, 'localhost')
        )
        mock_thread_instance.start.assert_called_once_with()
        self.assertEqual(result, None)

    def test_send_message_no_recieve_socket(self) -> None:
        '''
        test when the reciever socket not in system
        '''
        message = {'to': 22}

        result = self.server.send_message(message)

        self.assertFalse(result)
        self.assertEqual(result, False)

    @patch('server.json.dumps')
    def test_send_message_with_recieve_socket(self,
                                              mock_json: MagicMock) -> None:
        '''
        test the send message with reciever sockt availabe
        '''
        mock_json_data = MagicMock()
        mock_reciever_socket = MagicMock()
        mock_json.return_value = mock_json_data

        message = {'to': 22, 'text': 'writing unittests'}
        self.server.clients = {22: mock_reciever_socket}

        result = self.server.send_message(message)

        mock_json.assert_called_once()
        mock_reciever_socket.send.assert_called_once()
        mock_json_data.encode.assert_called_once_with('utf-8')
        self.assertTrue(result)
        self.assertEqual(result, True)

    @patch('server.Server.message_logger')
    @patch('server.json.dumps')
    def test_send_message_with_exception(self,
                                         mock_json: MagicMock,
                                         mock_message_logger: MagicMock,
                                         ) -> None:
        '''
        test the send message with reciever sockt availabe and
        and exception is raised
        '''
        mock_json_data = MagicMock()
        mock_reciever_socket = MagicMock()
        mock_json.return_value = mock_json_data
        mock_reciever_socket.send.side_effect = ValueError('Wrong format')

        message = {'to': 22, 'text': 'writing unittests'}
        self.server.clients = {22: mock_reciever_socket}

        result = self.server.send_message(message)

        mock_json.assert_called_once()
        mock_reciever_socket.send.assert_called_once()
        mock_json_data.encode.assert_called_once_with('utf-8')
        self.assertEqual(result, False)
        self.assertNotIn(22, self.server.clients)
        mock_message_logger.assert_called_once_with('Error : 22 Not connected')

    def test_handle_client(self) -> None:
        '''
        test the handle client when the message is empty
        '''
        client_socket = MagicMock()
        client_socket.recv.return_value = b''
        self.server.connected = True

        result = self.server.handle_client(client_socket, 'localhost')

        self.assertTrue(client_socket.recv.called)
        self.assertTrue(client_socket.close.called)
        self.assertFalse(result)

    def test_handle_client_connected_false(self) -> None:
        '''
        test the handle client when the message is empty
        '''
        client_socket = MagicMock()
        self.server.connected = False
        result = self.server.handle_client(client_socket, 'localhost')

        self.assertFalse(client_socket.recv.called)
        self.assertFalse(client_socket.close.called)
        self.assertFalse(result)

    @patch('server.Server.send_message')
    @patch('server.json.loads')
    def test_handle_client_with_message(
        self, mock_jsonload: MagicMock, mock_sendmessage: MagicMock
    ) -> None:
        '''
        test the handle client when the message is empty
        '''
        client_socket = MagicMock()
        client_socket.recv.side_effect = [
            b'{"from": 33, "to": 44, "text": "Hello"}',  # First message
            b''
        ]
        mock_jsonload.return_value = {'from': 33, 'to': 44, 'text': 'Hello'}
        self.server.connected = True
        result = self.server.handle_client(client_socket, 'localhost')

        self.assertEqual(client_socket.recv.call_count, 2)
        self.assertTrue(client_socket.close.call_count, 1)
        self.assertFalse(result)
        mock_jsonload.assert_called_with(
            '{"from": 33, "to": 44, "text": "Hello"}')
        mock_sendmessage.assert_called_once_with(
            {'from': 33, 'to': 44, 'text': 'Hello'})

    @patch('server.Server.send_message')
    @patch('server.json.loads')
    def test_handle_client_Send_message_return_false(
        self, mock_jsonload: MagicMock, mock_sendmessage: MagicMock
    ) -> None:
        '''
        test the handle client when the message is empty
        '''
        client_socket = MagicMock()
        client_socket.recv.side_effect = [
            b'{"from": 33, "to": 44, "text": "Hello"}',  # First message
            b''
        ]
        mock_jsonload.return_value = {'from': 33, 'to': 44, 'text': 'Hello'}
        self.server.connected = True
        mock_sendmessage.return_value = False

        result = self.server.handle_client(client_socket, 'localhost')

        self.assertEqual(client_socket.recv.call_count, 2)
        self.assertTrue(client_socket.close.call_count, 1)
        self.assertFalse(result)
        mock_jsonload.assert_called_with(
            '{"from": 33, "to": 44, "text": "Hello"}')
        mock_sendmessage.assert_called_once_with(
            {'from': 33, 'to': 44, 'text': 'Hello'})

        client_socket.send.assert_called_once_with(
            b'Phone number your sennt to no registered')

    @patch('server.Server.create_server')
    def test_start_server(self,
                          mock_create_server: MagicMock
                          ) -> None:
        '''
        test when connected is set to false
        '''
        self.server.connected = False
        self.server.start_server()
        mock_create_server.assert_called_once()
