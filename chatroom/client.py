import asyncio
import sys

async def receive_messages(reader):
    """Function to continuously receive messages from server"""
    try:
        while True:
            data = await reader.read(2048)
            if not data:
                print("Lost connection to server")
                return
            print(data.decode('utf-8'))
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"Error receiving messages: {e}")
        return

async def send_messages(writer):
    """Function to send user input to server"""
    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, input)
            writer.write(message.encode('utf-8'))
            await writer.drain()
            
            if message == "/quit":
                return
    except asyncio.CancelledError:
        return
    except Exception as e:
        print(f"Error sending messages: {e}")
        return

async def main():
    if len(sys.argv) != 3:
        print("Correct usage: script, IP address, port number")
        return
        
    IP_address = str(sys.argv[1])
    Port = int(sys.argv[2])
    
    try:
        reader, writer = await asyncio.open_connection(IP_address, Port)
        print(f"Connected to {IP_address}:{Port}")
        
        # Get first server message (welcome)
        welcome = await reader.read(2048)
        print(welcome.decode('utf-8'))
        
        # Send username
        username = input("Enter your username: ")
        writer.write(username.encode('utf-8'))
        await writer.drain()
        
        # Create tasks for sending and receiving
        recv_task = asyncio.create_task(receive_messages(reader))
        send_task = asyncio.create_task(send_messages(writer))
        
        print("Connected to the server. Type /help for commands.")
        
        # Wait for one of the tasks to complete (likely send_task when user types /quit)
        done, pending = await asyncio.wait(
            [recv_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel the remaining task
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except ConnectionRefusedError:
        print("Unable to connect to server")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'writer' in locals():
            writer.close()
            await writer.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient terminated by user")