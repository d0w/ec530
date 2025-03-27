import asyncio
import argparse
import uuid
import getpass
from network import PeerDiscovery, P2PConnection
from message import MessageManager
from database import DatabaseManager

class ChatApplication:
    """Main chat application class"""
    
    def __init__(self, username: str, db_dsn: str, discovery_port: int, p2p_port: int):
        self.user_id = str(uuid.uuid4())  # Generate unique ID
        self.username = username
        
        # Initialize components
        self.db_manager = DatabaseManager(db_dsn)
        self.p2p_connection = P2PConnection(port=p2p_port, user_id=self.user_id)
        self.peer_discovery = PeerDiscovery(port=discovery_port)
        self.message_manager = None
    
    async def initialize(self):
        """Initialize the application"""
        # Initialize database
        await self.db_manager.initialize()
        await self.db_manager.register_user(self.user_id, self.username)
        
        # Initialize message manager
        self.message_manager = MessageManager(
            self.user_id,
            self.db_manager,
            self.p2p_connection
        )
        
        # Add message handler
        self.message_manager.add_message_callback(self._handle_new_message)
        
        # Start peer discovery
        discovery_task = asyncio.create_task(
            self.peer_discovery.start_discovery(self.user_id)
        )

        async def start_p2p():
            await self.p2p_connection.start_server()
        
        # Start P2P server
        p2p_server_task = asyncio.create_task(start_p2p())

        await asyncio.sleep(1)
        
        print(f"Chat application initialized.")
        print(f"Your user ID: {self.user_id}")
        print(f"Your username: {self.username}")
        print(f"Your discovery port: {self.peer_discovery.port}")
        print(f"Your P2P port: {self.p2p_connection.port}")
        print("Waiting for peers...")
    
    def _handle_new_message(self, message):
        """Handle incoming messages"""
        print(f"\n[{message['timestamp']}] {message['sender_id']}: {message['content']}")
        print("> ", end="", flush=True)  # Reprint prompt
    
    async def connect_to_peer(self, peer_id: str, ip: str, port: int):
        """Connect to a specific peer"""
        if await self.p2p_connection.connect_to_peer(peer_id, ip, port):
            # Send pending messages
            await self.message_manager.send_pending_messages(peer_id)
            return True
        return False
    
    async def send_message(self, recipient_id: str, content: str):
        """Send a message to a recipient"""
        return await self.message_manager.send_message(recipient_id, content)
    
    async def get_conversation(self, peer_id: str, limit: int = 50):
        """Get conversation history with a peer"""
        return await self.message_manager.get_conversation(peer_id, limit)
    
    async def run_cli(self):
        """Run command-line interface"""

        # Async input
        async def get_input():
        # Use a separate thread for input to avoid blocking
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: input("> ").strip())
        
        print("Type 'help' for available commands.")
        print("> ", end="", flush=True)
        while True:
            command = await get_input()
            
            if command.lower() == "exit":
                break
                
            elif command.lower() == "peers":
                peers = self.peer_discovery.peers
                print("Online peers:")
                for peer_id, (ip, port) in peers.items():
                    print(f"  {peer_id} at {ip}:{port}")
            
            elif command.lower().startswith("connect "):
                _, peer_id, ip, port = command.split(maxsplit=3)
                if port.isdigit() and ip is not None: 
                    # print(f"Peer {peer_id} not found")
                    # add manually by ip and port
                    if await self.connect_to_peer(peer_id, ip, int(port)):
                        self.peer_discovery.peers[peer_id] = (ip, int(port))
                        print(f"Connected to {peer_id} at {ip}:{port}")

                    else:
                        print(f"Failed to connect to {peer_id}")

                elif peer_id in self.peer_discovery.peers:
                    ip, port = self.peer_discovery.peers[peer_id]
                    if await self.connect_to_peer(peer_id, ip, port):
                        print(f"Connected to {peer_id}")
                    else:
                        print(f"Failed to connect to {peer_id}")
                
                else:
                    print("Usage if running locally with user-set discovery ports: connect <peer_id> <ip> <port>")
                    

            
            elif command.lower().startswith("send "):
                parts = command.split(maxsplit=2)
                if len(parts) != 3:
                    print("Usage: send <peer_id> <message>")
                    continue
                
                _, peer_id, content = parts
                if peer_id not in self.peer_discovery.peers:
                    print(f"Peer {peer_id} not found")
                    continue
                sent = await self.send_message(peer_id, content)
                if sent:
                    print("Message sent directly")
                else:
                    print("Message queued for delivery when peer comes online")
            
            elif command.lower().startswith("history "):
                _, peer_id = command.split(maxsplit=1)
                messages = await self.get_conversation(peer_id)
                
                print(f"Conversation with {peer_id}:")
                for message in reversed(messages):
                    direction = ">>>" if message["sender_id"] == self.user_id else "<<<"
                    status = "(delivered)" if message["is_delivered"] else "(sent)" if message["is_sent"] else "(pending)"
                    print(f"{direction} [{message['timestamp']}] {status} {message['content']}")
            
            elif command.lower() == "help":
                print("Available commands:")
                print("  peers - List online peers")
                print("  connect <peer_id> - Connect to a peer")
                print("  send <peer_id> <message> - Send a message to a peer")
                print("  history <peer_id> - Show conversation history")
                print("  exit - Exit the application")
            
            else:
                print("Unknown command. Type 'help' for available commands.")


async def main():
    parser = argparse.ArgumentParser(description="P2P Chat Application")
    parser.add_argument("--username", help="Your username", default=None)
    parser.add_argument("--db", help="PostgreSQL connection string", 
                      default="postgresql://postgres:postgres@localhost/p2p_chat")
    parser.add_argument("--discovery-port", type=int, default=5000, help="Port for peer discovery")
    parser.add_argument("--p2p-port", type=int, default=5001, help="Port for P2P connections")
    
    args = parser.parse_args()
    username = args.username if args.username else input("Enter your username: ")
    
    app = ChatApplication(username, args.db, args.discovery_port, args.p2p_port)
    await app.initialize()
    
    # Run CLI interface
    await app.run_cli()


if __name__ == "__main__":
    asyncio.run(main())