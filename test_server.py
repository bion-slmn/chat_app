
from unittest.mock import patch, MagicMock, call
from server import Server
import unittest


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
