import asyncio
import json
import uuid
import time
import hashlib
from typing import Dict, List, Set, Optional

class Node:
    def __init__(self, host: str, port: int, username: str):
        self.host = host
        self.port = port
        self.username = username
        self.node_id = hashlib.sha1(f"{host}:{port}:{username}".encode()).hexdigest()
        
        # Known peers: {node_id: (host, port, username)}
        self.peers: Dict[str, tuple] = {}
        # Connected peers with active sessions
        self.connections: Dict[str, asyncio.StreamWriter] = {}
        # Message history
        self.messages: Dict[str, List[dict]] = {}
        # DHT storage (node_id -> (host, port, username))
        self.dht_store: Dict[str, tuple] = {}
        
    async def start(self):
        """Start the node server and bootstrap if needed"""
        # Start TCP server for messages
        self.server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        
        print(f"Node {self.username} listening on {self.host}:{self.port}")
        
        # Schedule periodic tasks
        asyncio.create_task(self._periodic_cleanup())
        asyncio.create_task(self._periodic_discovery())
        
        async with self.server:
            await self.server.serve_forever()
    
    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming TCP connections"""
        peer_addr = writer.get_extra_info('peername')
        print(f"Connection from {peer_addr}")
        
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                    
                message = json.loads(data.decode())
                await self._process_message(message, writer)
                
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"Connection from {peer_addr} closed")
    
    async def _process_message(self, message: dict, writer: asyncio.StreamWriter):
        """Process incoming messages based on type"""
        msg_type = message.get("type")
        
        if msg_type == "hello":
            # Handle peer introduction
            peer_id = message.get("node_id")
            username = message.get("username")
            host = message.get("host") 
            port = message.get("port")
            
            self.peers[peer_id] = (host, port, username)
            self.connections[peer_id] = writer
            
            # Send acknowledgment
            await self._send_message({
                "type": "hello_ack",
                "node_id": self.node_id,
                "username": self.username
            }, writer)
            
        elif msg_type == "chat":
            # Handle chat message
            sender_id = message.get("sender_id")
            sender_name = message.get("sender_name")
            content = message.get("content")
            timestamp = message.get("timestamp")
            
            if sender_id not in self.messages:
                self.messages[sender_id] = []
                
            self.messages[sender_id].append({
                "sender": sender_name,
                "content": content,
                "timestamp": timestamp
            })
            
            print(f"Message from {sender_name}: {content}")
            
            # Send acknowledgment
            await self._send_message({
                "type": "message_ack",
                "message_id": message.get("message_id")
            }, writer)
            
        elif msg_type == "find_node":
            # DHT node lookup
            target_id = message.get("target_id")
            if target_id in self.dht_store:
                await self._send_message({
                    "type": "find_node_reply",
                    "target_id": target_id,
                    "found": True,
                    "node_info": self.dht_store[target_id]
                }, writer)
            else:
                # Return closest nodes we know
                await self._send_message({
                    "type": "find_node_reply",
                    "target_id": target_id,
                    "found": False,
                    "closest_nodes": self._get_closest_nodes(target_id, 3)
                }, writer)
        
        elif msg_type == "store":
            # Store DHT data
            key = message.get("key")
            value = message.get("value")
            self.dht_store[key] = value
            
            await self._send_message({
                "type": "store_ack",
                "key": key
            }, writer)
    
    async def _send_message(self, message: dict, writer: asyncio.StreamWriter):
        """Send a message through an established connection"""
        data = json.dumps(message).encode() + b'\n'
        writer.write(data)
        await writer.drain()
    
    async def connect_to_peer(self, host: str, port: int):
        """Establish connection to a new peer"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Send hello message
            await self._send_message({
                "type": "hello",
                "node_id": self.node_id,
                "username": self.username,
                "host": self.host,
                "port": self.port
            }, writer)
            
            # Start task to handle responses
            asyncio.create_task(self._handle_peer_connection(reader, writer))
            
            return True
        except Exception as e:
            print(f"Failed to connect to peer {host}:{port}: {e}")
            return False
    
    async def _handle_peer_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle an outgoing peer connection"""
        peer_addr = writer.get_extra_info('peername')
        print(f"Connected to peer {peer_addr}")
        
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                
                message = json.loads(data.decode())
                
                if message.get("type") == "hello_ack":
                    # Got acknowledgment, save the connection
                    peer_id = message.get("node_id")
                    username = message.get("username")
                    host, port = peer_addr
                    
                    self.peers[peer_id] = (host, port, username)
                    self.connections[peer_id] = writer
                    print(f"Registered peer {username} ({peer_id})")
                else:
                    # Process other message types
                    await self._process_message(message, writer)
        
        except Exception as e:
            print(f"Error in peer connection: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            print(f"Connection to {peer_addr} closed")
    
    async def send_chat_message(self, peer_id: str, content: str):
        """Send a chat message to a specific peer"""
        if peer_id not in self.connections:
            # Try to find and connect to the peer
            if peer_id in self.peers:
                host, port, _ = self.peers[peer_id]
                success = await self.connect_to_peer(host, port)
                if not success:
                    return False
            else:
                # Try to find the peer through DHT
                found = await self._find_node(peer_id)
                if not found:
                    return False
        
        message = {
            "type": "chat",
            "message_id": str(uuid.uuid4()),
            "sender_id": self.node_id,
            "sender_name": self.username,
            "content": content,
            "timestamp": time.time()
        }
        
        await self._send_message(message, self.connections[peer_id])
        return True
    
    async def _find_node(self, node_id: str) -> bool:
        """Find a node in the DHT network"""
        # Implementation of Kademlia-like lookup
        # For simplicity, just try known peers
        for peer_id, (host, port, _) in self.peers.items():
            if peer_id not in self.connections:
                success = await self.connect_to_peer(host, port)
                if not success:
                    continue
            
            # Ask this peer about the target node
            writer = self.connections[peer_id]
            await self._send_message({
                "type": "find_node",
                "target_id": node_id
            }, writer)
            
            # In a real implementation, wait for and process the response
            # This is simplified
            
        return False  # Not found
    
    def _get_closest_nodes(self, target_id: str, count: int) -> List[tuple]:
        """Get closest nodes to a target ID based on XOR distance"""
        # Simplified implementation - in a real system use XOR metric
        return list(self.peers.items())[:count]
    
    async def _periodic_cleanup(self):
        """Periodic task to clean up stale connections"""
        while True:
            await asyncio.sleep(60)  # Run every minute
            # Clean up logic here
    
    async def _periodic_discovery(self):
        """Periodic task to discover new peers"""
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            # Discovery logic here
    
    async def bootstrap(self, known_host: str, known_port: int):
        """Bootstrap this node by connecting to a known peer"""
        success = await self.connect_to_peer(known_host, known_port)
        if success:
            print(f"Successfully bootstrapped with {known_host}:{known_port}")
        else:
            print(f"Failed to bootstrap with {known_host}:{known_port}")
