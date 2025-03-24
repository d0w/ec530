import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import io
import socket

# Import the server module
sys.path.insert(0, '/Users/derek/Documents/CSWork/EC530/ec530/chatroom')
import server

@pytest.fixture
def reset_clients():
    """Reset the clients dict before each test"""
    server.clients = {}
    yield
    server.clients = {}

class MockStreamWriter:
    def __init__(self):
        self.written_data = []
        self.closed = False
    
    def write(self, data):
        self.written_data.append(data)
    
    async def drain(self):
        pass
    
    def close(self):
        self.closed = True
    
    async def wait_closed(self):
        pass
    
    def get_extra_info(self, info):
        if info == 'peername':
            return ('127.0.0.1', 12345)
        return None

class MockStreamReader:
    def __init__(self, data_to_return=None):
        self.data = data_to_return if data_to_return else []
        self.index = 0
    
    async def read(self, n):
        if self.index >= len(self.data):
            # Simulate connection closed
            return b''
        data = self.data[self.index]
        self.index += 1
        return data if isinstance(data, bytes) else data.encode('utf-8')

@pytest.mark.asyncio
async def test_send_message_to_client_success():
    """Test sending a message to a client successfully"""
    writer = MockStreamWriter()
    result = await server.send_message_to_client(writer, "Test message")
    
    assert result is True
    assert writer.written_data == [b"Test message"]
    assert writer.closed is False

@pytest.mark.asyncio
async def test_send_message_to_client_failure():
    """Test handling error when sending a message"""
    writer = MockStreamWriter()
    writer.write = Mock(side_effect=Exception("Connection error"))
    
    result = await server.send_message_to_client(writer, "Test message")
    
    assert result is False
    assert writer.closed is True

@pytest.mark.asyncio
async def test_handle_private_message_invalid_format(reset_clients):
    """Test handling private message with invalid format"""
    writer = MockStreamWriter()
    await server.handle_private_message("user1", "invalid message", writer)
    
    assert b"To send a private message, use: @username message" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_private_message_missing_content(reset_clients):
    """Test handling private message with missing content"""
    writer = MockStreamWriter()
    await server.handle_private_message("user1", "@user2", writer)
    
    assert b"ERROR: Message content is empty" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_private_message_user_not_found(reset_clients):
    """Test handling private message when recipient doesn't exist"""
    writer = MockStreamWriter()
    await server.handle_private_message("user1", "@nonexistent Hello there", writer)
    
    assert b"ERROR: User nonexistent not found" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_private_message_success(reset_clients):
    """Test successful private message handling"""
    sender_writer = MockStreamWriter()
    recipient_writer = MockStreamWriter()
    
    # Set up the mock clients
    server.clients = {
        "user1": {"writer": sender_writer},
        "user2": {"writer": recipient_writer}
    }
    
    await server.handle_private_message("user1", "@user2 Hello there", sender_writer)
    
    # Check recipient received the message
    assert b"[From user1]: Hello there" in recipient_writer.written_data[0]
    
    # Check sender received confirmation
    assert b"[To user2]: Hello there" in sender_writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_command_users(reset_clients):
    """Test /users command"""
    writer = MockStreamWriter()
    server.clients = {"user1": {}, "user2": {}}
    
    await server.handle_command("user1", "/users", writer)
    
    assert b"Online users: user1, user2" in writer.written_data[0] or b"Online users: user2, user1" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_command_help(reset_clients):
    """Test /help command"""
    writer = MockStreamWriter()
    
    await server.handle_command("user1", "/help", writer)
    
    # Check for parts of the help text
    assert b"Available commands:" in writer.written_data[0]
    assert b"@username message" in writer.written_data[0]
    assert b"/users" in writer.written_data[0]
    assert b"/quit" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_command_unknown(reset_clients):
    """Test unknown command"""
    writer = MockStreamWriter()
    
    await server.handle_command("user1", "/unknown", writer)
    
    assert b"Unknown command: /unknown" in writer.written_data[0]

@pytest.mark.asyncio
async def test_handle_client_username_taken(reset_clients):
    """Test connection rejected when username is taken"""
    reader = MockStreamReader(["existinguser"])
    writer = MockStreamWriter()
    
    # Set up existing user
    server.clients = {"existinguser": {"reader": None, "writer": None, "addr": None}}
    
    await server.handle_client(reader, writer)
    
    assert b"ERROR: Username already taken" in writer.written_data[1]
    assert writer.closed is True

@pytest.mark.asyncio
async def test_handle_client_connect_and_disconnect(reset_clients):
    """Test client connection and disconnection flow"""
    reader = MockStreamReader(["newuser", "/quit"])
    writer = MockStreamWriter()
    
    await server.handle_client(reader, writer)
    
    # Check welcome messages were sent
    assert b"Welcome! Please enter your username:" in writer.written_data[0]
    assert b"Welcome newuser!" in writer.written_data[1]
    
    # Check client was added then removed from clients dict
    assert "newuser" not in server.clients

@pytest.mark.asyncio
async def test_main_with_invalid_args():
    """Test main function with invalid arguments"""
    sys.argv = ["server.py"]  # Not enough arguments
    
    # Redirect stdout to capture print output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    await server.main()
    
    sys.stdout = sys.__stdout__  # Reset stdout
    
    assert "Correct usage: script, IP address, port number" in captured_output.getvalue()

@pytest.mark.asyncio
@patch('asyncio.start_server')
async def test_main_with_valid_args(mock_start_server):
    """Test main function with valid arguments"""
    sys.argv = ["server.py", "127.0.0.1", "8000"]
    
    # Setup mock server
    mock_server = AsyncMock()
    mock_socket = MagicMock()
    mock_socket.getsockname.return_value = ('127.0.0.1', 8000)
    mock_server.sockets = [mock_socket]
    mock_start_server.return_value = mock_server
    
    # Mock serve_forever to avoid blocking
    mock_server.serve_forever = AsyncMock(side_effect=KeyboardInterrupt)
    
    # Redirect stdout to capture print output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        await server.main()
    except KeyboardInterrupt:
        pass
    
    sys.stdout = sys.__stdout__  # Reset stdout
    
    # Check server was started with correct parameters
    mock_start_server.assert_called_once_with(
        server.handle_client, '127.0.0.1', 8000
    )
    assert "Server running on 127.0.0.1:8000" in captured_output.getvalue()