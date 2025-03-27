import asyncio
import json
import socket
from typing import Dict, List, Callable, Any

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeerDiscovery:
    """Handles peer discovery using UDP broadcast"""
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.peers = {}  # {peer_id: (ip, port)}
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
    async def start_discovery(self, user_id: str):
        """Broadcast presence and listen for other peers"""
        # Set up listener
        discovery_server = await asyncio.start_server(
            self._handle_peer_connection,
            '0.0.0.0', 
            self.port
        )
        
        # Periodically broadcast presence
        while True:
            # self._broadcast_presence(user_id)
            await asyncio.sleep(60)  # Broadcast every minute
    
    def _broadcast_presence(self, user_id: str):
        """Broadcast presence to the network"""
        message = json.dumps({
            "type": "discovery",
            "user_id": user_id,
            "port": self.port
        }).encode()
        self.broadcast_socket.sendto(message, ('<broadcastnotsetfornow>', self.port))
    
    async def _handle_peer_connection(self, reader, writer):
        """Handle incoming peer connection"""
        data = await reader.read(1024)
        message = json.loads(data.decode())

        
        
        if message.get("type") == "discovery":
            peer_id = message.get("user_id")
            addr = writer.get_extra_info('peername')
            self.peers[peer_id] = (addr[0], message.get("port"))
        
        writer.close()
        await writer.wait_closed()


class P2PConnection:
    """Manages direct connections between peers"""
    
    def __init__(self, port: int = 5001, user_id: str = None):
        self.user_id = user_id
        self.port = port
        self.message_handlers = []
        self.active_connections = {}  # {peer_id: (reader, writer)}
    
    async def start_server(self):
        """Start listening for incoming connections"""
        ip = "0.0.0.0"
        server = await asyncio.start_server(
            self._handle_connection,
            ip,
            self.port
        )

        logger.info(f"Listening for incoming connections on {ip}:{self.port}...")
        
        async with server:
            await server.serve_forever()
    
    async def connect_to_peer(self, peer_id: str, ip: str, port: int):
        """Establish connection to a peer"""
        try:
            logger.info(f"Connecting to peer {peer_id} at {ip}:{port}...")
            reader, writer = await asyncio.open_connection(ip, port)
            self.active_connections[peer_id] = (reader, writer)

            identity_message = {
                "type": "identity",
                "user_id": self.user_id
            }

            writer.write(json.dumps(identity_message).encode())
            await writer.drain()
            
            # Start a task to handle messages from this peer
            asyncio.create_task(self._read_messages(peer_id, reader))
            return True
        except Exception as e:
            logger.info(f"Failed to connect to peer {peer_id}: {e}")
            return False
    
    async def _handle_connection(self, reader, writer):
        """Handle incoming connection"""
        # First message should identify the peer
        addr = writer.get_extra_info('peername')
        logger.info(f"Incoming connection from {addr}")

        try:
            data = await reader.read(1024)
            logger.info(f"Received data: {data}")
            
            if not data:
                logger.info("No data received, closing connection")
                writer.close()
                return
                
            message = json.loads(data.decode())
            logger.info(f"Decoded message: {message}")
            
            if message.get("type") == "identity":
                peer_id = message.get("user_id")
                logger.info(f"Identified peer: {peer_id}")
                self.active_connections[peer_id] = (reader, writer)

                confirmation = {
                    "type": "identity_confirmation",
                    "message": "Connected successfully"
                }

                writer.write(json.dumps(confirmation).encode())
                await writer.drain()
                logger.info(f"Sent confirmation to {peer_id}")
                
                # Start a task to handle messages from this peer
                asyncio.create_task(self._read_messages(peer_id, reader))
            else:
                logger.info(f"Unexpected message type: {message.get('type')}")
        except Exception as e:
            logger.info(f"Error handling connection: {e}")
        
    async def _read_messages(self, peer_id: str, reader):
        """Read messages from a connected peer"""
        logger.info("Reading messages")
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                    
                message = json.loads(data.decode())
                
                logger.info(f"Message: {message}")
                
                # Notify all message handlers
                for handler in self.message_handlers:
                    if asyncio.iscoroutinefunction(handler):
                            # If handler is async, await it
                        await handler(peer_id, message)
                    else:
                        # If handler is synchronous, just call it
                        handler(peer_id, message)
                    
        except Exception as e:
            logger.info(f"Error reading from {peer_id}: {e}")
        finally:
            # Connection closed
            if peer_id in self.active_connections:
                del self.active_connections[peer_id]
    
    async def send_message(self, peer_id: str, message: Dict):
        """Send a message to a specific peer"""
        if peer_id in self.active_connections:
            _, writer = self.active_connections[peer_id]
            data = json.dumps(message).encode()
            writer.write(data)
            await writer.drain()
            logger.info(f"Sent message to {peer_id}: {message}")
            return True
        return False
    
    def add_message_handler(self, handler: Callable[[str, Dict], Any]):
        """Add a handler for incoming messages"""
        self.message_handlers.append(handler)