import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
import sys
import io
import builtins

# Import the client module
sys.path.insert(0, '/Users/derek/Documents/CSWork/EC530/ec530/chatroom')
import client

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
async def test_receive_messages_normal_flow():
    """Test receive_messages with normal message flow"""
    reader = MockStreamReader(["Hello", "World", "Testing"])
    
    # Capture printed output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    # Create a task for the function we're testing
    task = asyncio.create_task(client.receive_messages(reader))
    
    # Let it run a bit
    await asyncio.sleep(0.1)
    
    # Cancel the task since it's in an infinite loop
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Reset stdout
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    # Check output
    assert "Hello" in output
    assert "World" in output
    assert "Testing" in output

@pytest.mark.asyncio
async def test_receive_messages_connection_lost():
    """Test receive_messages when connection is lost"""
    # Empty data list will cause read to return empty bytes
    reader = MockStreamReader([])
    
    # Capture printed output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    await client.receive_messages(reader)
    
    # Reset stdout
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert "Lost connection to server" in output

@pytest.mark.asyncio
async def test_receive_messages_error():
    """Test receive_messages with an error"""
    reader = MagicMock()
    reader.read = AsyncMock(side_effect=Exception("Test error"))
    
    # Capture printed output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    await client.receive_messages(reader)
    
    # Reset stdout
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert "Error receiving messages: Test error" in output

@pytest.mark.asyncio
@patch('builtins.input', side_effect=['Hello', 'World', '/quit'])
async def test_send_messages_normal_flow(mock_input):
    """Test send_messages with normal message flow"""
    writer = MockStreamWriter()
    
    await client.send_messages(writer)
    
    assert writer.written_data == [b'Hello', b'World', b'/quit']

@pytest.mark.asyncio
async def test_send_messages_error():
    """Test send_messages with an error"""
    writer = MagicMock()
    writer.drain = AsyncMock(side_effect=Exception("Test error"))
    
    with patch('builtins.input', return_value='Hello'):
        # Capture printed output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        await client.send_messages(writer)
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        assert "Error sending messages: Test error" in output

@pytest.mark.asyncio
async def test_main_invalid_args():
    """Test main function with invalid arguments"""
    sys.argv = ["client.py"]  # Not enough arguments
    
    # Capture printed output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    await client.main()
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert "Correct usage: script, IP address, port number" in output

@pytest.mark.asyncio
@patch('asyncio.open_connection')
@patch('builtins.input', side_effect=['testuser', 'message1', '/quit'])
async def test_main_normal_flow(mock_input, mock_open_connection):
    """Test main function with normal flow"""
    sys.argv = ["client.py", "127.0.0.1", "8000"]
    
    # Setup mocks
    reader = MockStreamReader(["Welcome message"])
    writer = MockStreamWriter()
    mock_open_connection.return_value = (reader, writer)
    
    # Setup a mock Wait function to simulate the first task completing
    original_wait = asyncio.wait
    
    async def mock_wait(aws, **kwargs):
        # Wait a bit to allow tasks to start
        await asyncio.sleep(0.1)
        # Return the send_task as done to simulate user typing /quit
        send_task = [t for t in aws if t._coro.__name__ == 'send_messages'][0]
        remaining = [t for t in aws if t != send_task]
        return {send_task}, set(remaining)
    
    # Patch asyncio.wait
    with patch('asyncio.wait', mock_wait):
        # Capture printed output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        await client.main()
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
    # Check open_connection was called with correct args
    mock_open_connection.assert_called_once_with("127.0.0.1", 8000)
    
    # Check welcome message was printed
    assert "Welcome message" in output
    
    # Check username was sent
    assert b'testuser' in writer.written_data
    
    # Check connection message
    assert "Connected to 127.0.0.1:8000" in output

@pytest.mark.asyncio
async def test_main_connection_refused():
    """Test main function when connection is refused"""
    sys.argv = ["client.py", "127.0.0.1", "8000"]
    
    # Setup mock for open_connection
    with patch('asyncio.open_connection', side_effect=ConnectionRefusedError):
        # Capture printed output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        await client.main()
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
    assert "Unable to connect to server" in output

@pytest.mark.asyncio
@patch('asyncio.open_connection')
async def test_main_general_exception(mock_open_connection):
    """Test main function with a general exception"""
    sys.argv = ["client.py", "127.0.0.1", "8000"]
    
    # Setup mock for open_connection to raise exception
    mock_open_connection.side_effect = Exception("General test error")
    
    # Capture printed output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    await client.main()
    
    # Reset stdout
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert "Error: General test error" in output
