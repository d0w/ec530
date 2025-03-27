import asyncio
import socket
import sys

# store client connections with usernames as keys
clients = {}

async def send_message_to_client(writer, message):
    """Send a message to a specific client"""
    try:
        writer.write(message.encode('utf-8'))
        await writer.drain()
        return True
    except:
        writer.close()
        return False

async def handle_private_message(sender, message_text, writer):
    """Handle direct messages between users"""
    if not message_text.startswith('@'):
        await send_message_to_client(writer, "To send a private message, use: @username message")
        return
    
    try:
        # parse recipient and message
        parts = message_text.split(' ', 1)
        recipient = parts[0][1:]  # Remove the @ symbol
        
        if len(parts) < 2:
            await send_message_to_client(writer, "ERROR: Message content is empty")
            return
            
        content = parts[1]
        
        # check if recipient exists
        if recipient in clients:
            recipient_writer = clients[recipient]['writer']
            # send to recipient
            await send_message_to_client(recipient_writer, f"[From {sender}]: {content}")
            # confirm to sender
            await send_message_to_client(writer, f"[To {recipient}]: {content}")
        else:
            await send_message_to_client(writer, f"ERROR: User {recipient} not found")
    except Exception as e:
        await send_message_to_client(writer, f"ERROR: {str(e)}")

async def handle_command(sender, command, writer):
    """Handle various commands from users"""
    if command == "/users":
        user_list = ", ".join(clients.keys())
        await send_message_to_client(writer, f"Online users: {user_list}")
    elif command == "/help":
        help_text = """
Available commands:
@username message - Send private message to user
/users - List all online users
/quit - Disconnect from server
        """
        await send_message_to_client(writer, help_text)
    else:
        await send_message_to_client(writer, f"Unknown command: {command}. Type /help for available commands.")

async def handle_client(reader, writer):
    """Handle client connection and messages"""
    addr = writer.get_extra_info('peername')
    print(f"New connection from {addr[0]}:{addr[1]}")
    
    await send_message_to_client(writer, "Welcome! Please enter your username:")
    
    # get username
    username_data = await reader.read(2048)
    username = username_data.decode('utf-8').strip()
    
    # check if username exists
    if username in clients:
        await send_message_to_client(writer, "ERROR: Username already taken. Please reconnect with a different name.")
        writer.close()
        await writer.wait_closed()
        return
    
    # register client
    clients[username] = {
        'reader': reader,
        'writer': writer,
        'addr': addr
    }
    
    await send_message_to_client(writer, f"Welcome {username}! To chat with someone, type @username message")
    
    # notify all users about new user
    for name, client_data in clients.items():
        if name != username:
            await send_message_to_client(client_data['writer'], f"SERVER: {username} has connected")
            await send_message_to_client(writer, f"SERVER: {name} is online")
    
    # main loop to handle client messages
    try:
        while True:
            data = await reader.read(2048)
            if not data:  # Client closed the connection
                break
                
            message = data.decode('utf-8').strip()
            print(f"{username}: {message}")
            
            if message.startswith('@'):
                # Handle private message
                await handle_private_message(username, message, writer)
            elif message.startswith('/'):
                # Handle command
                if message == '/quit':
                    break
                await handle_command(username, message, writer)
            else:
                await send_message_to_client(writer, "To send a message, use @username message format")
                
    except Exception as e:
        print(f"Error with client {username}: {e}")
    finally:
        # remove client from dictionary
        if username in clients:
            del clients[username]
        
        # nitify other users
        for name, client_data in clients.items():
            await send_message_to_client(client_data['writer'], f"SERVER: {username} has disconnected")
        
        print(f"{addr[0]}:{addr[1]} ({username}) disconnected")
        writer.close()
        await writer.wait_closed()

async def main():
    if len(sys.argv) != 3:
        print("Correct usage: script, IP address, port number")
        return
    
    IP_address = str(sys.argv[1])
    Port = int(sys.argv[2])
    
    # Start server
    server = await asyncio.start_server(
        handle_client, IP_address, Port)
    
    addr = server.sockets[0].getsockname()
    print(f'Server running on {addr[0]}:{addr[1]}')
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down server...")