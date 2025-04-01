import asyncio
import json
import argparse
import socket
import sys
from peer import Peer

async def run_cli(peer: Peer):
    """Interactive CLI for the peer"""
    print("\nWelcome to P2P Chat!")
    print("Commands:")
    print("  /list - List known peers")
    print("  /msg <peer_id> <message> - Send a direct message")
    print("  /inbox - Show received messages")
    print("  /quit - Quit the program")
    
    while True:
        try:
            command = await asyncio.to_thread(input, "\n> ")
            
            if command.startswith("/list"):
                peer.list_known_peers()
                
            elif command.startswith("/msg "):
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    print("Usage: /msg <peer_id> <message>")
                    continue
                    
                peer_id = parts[1]
                message = parts[2]
                
                await peer.send_message(peer_id, message)
                
            elif command.startswith("/inbox"):
                peer.list_messages()
                
            elif command.startswith("/quit"):
                print("Exiting...")
                sys.exit(0)
                
            else:
                print("Unknown command. Type /help for commands.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
            
        except Exception as e:
            print(f"Error: {e}")

async def main():
    # Get local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    
    parser = argparse.ArgumentParser(description='P2P Chat')
    parser.add_argument('--host', type=str, default=local_ip, help='Host IP')
    parser.add_argument('--port', type=int, default=8000, help='Port number')
    parser.add_argument('--username', type=str, required=True, help='Your username')
    parser.add_argument('--connect', type=str, help='IP:port of a peer to connect to')
    
    args = parser.parse_args()
    
    peer = Peer(args.host, args.port, args.username)
    
    # If a peer to connect to was provided, add it to known peers
    if args.connect:
        try:
            connect_host, connect_port = args.connect.split(':')
            connect_port = int(connect_port)
            
            # Add a temporary entry
            temp_peer_id = "temp"
            peer.known_peers[temp_peer_id] = (connect_host, connect_port, "unknown")
            
            # Start server and CLI
            server_task = asyncio.create_task(peer.start())
            
            # Wait a moment for the server to start
            await asyncio.sleep(1)
            
            # Do discovery to get the actual peer ID
            try:
                await peer.discover_peers(connect_host, connect_port)
                # Remove temporary entry
                if temp_peer_id in peer.known_peers:
                    peer.known_peers.pop(temp_peer_id)
            except Exception as e:
                print(f"Failed to connect to initial peer: {e}")
            
            # Start the CLI
            cli_task = asyncio.create_task(run_cli(peer))
            
            # Wait for both to complete (which would only happen on error)
            await asyncio.gather(server_task, cli_task)
            
        except ValueError:
            print("Invalid connect address. Use format IP:port")
            return
    else:
        # Start the server
        server_task = asyncio.create_task(peer.start())
        
        # Start the CLI
        cli_task = asyncio.create_task(run_cli(peer))
        
        # Wait for both to complete (which would only happen on error)
        await asyncio.gather(server_task, cli_task)

if __name__ == "__main__":
    asyncio.run(main())