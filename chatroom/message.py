import asyncio
import datetime
import json
from typing import Dict, List, Optional
from network import P2PConnection
from database import DatabaseManager

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageManager:
    """Manages message sending, receiving, and storage"""
    
    def __init__(self, user_id: str, db_manager: DatabaseManager, p2p: P2PConnection):
        self.user_id = user_id
        self.db = db_manager
        self.p2p = p2p
        self.message_callbacks = []
        
        # Register as message handler
        self.p2p.add_message_handler(self._handle_incoming_message)
    
    async def send_message(self, recipient_id: str, content: str) -> bool:
        """Send a message to a recipient"""
        # Create message object
        message = {
            "type": "chat_message",
            "sender_id": self.user_id,
            "recipient_id": recipient_id,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat(),
            "message_id": f"{self.user_id}-{int(datetime.datetime.now().timestamp())}"
        }
        
        # Try to send directly if peer is connected
        sent = await self.p2p.send_message(recipient_id, message)
        
        # If failed to send directly, store as pending
        if not sent:
            logger.info(f"Failed to send message to {recipient_id}, storing as pending.")
            await self.db.store_pending_message(
                message_id=message["message_id"],
                sender_id=self.user_id,
                recipient_id=recipient_id,
                content=content,
                timestamp=message["timestamp"]
            )
            
        # Store in local message history
        logger.info(f"Storing message in local history: {message}")
        await self.db.store_message(
            message_id=message["message_id"],
            sender_id=self.user_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=message["timestamp"],
            is_sent=sent
        )
        
        return sent
    
    async def _handle_incoming_message(self, sender_id: str, message: Dict):
        """Process incoming messages"""
        if message.get("type") == "chat_message":
            # Store message in database
            logger.info(f"Storing message from {sender_id}: {message}")
            await self.db.store_message(
                message_id=message["message_id"],
                sender_id=message["sender_id"],
                recipient_id=message["recipient_id"],
                content=message["content"],
                timestamp=message["timestamp"],
                is_sent=True
            )
            
            # Send delivery confirmation
            await self.p2p.send_message(sender_id, {
                "type": "delivery_confirmation",
                "message_id": message["message_id"],
                "recipient_id": self.user_id
            })
            
            # Notify application about new message
            for callback in self.message_callbacks:
                callback(message)
        
        elif message.get("type") == "delivery_confirmation":
            # Update message status in database
            await self.db.mark_message_delivered(message["message_id"])
    
    async def send_pending_messages(self, recipient_id: str):
        """Try to send any pending messages for a recipient"""
        pending_messages = await self.db.get_pending_messages(recipient_id)
        
        for msg in pending_messages:
            message = {
                "type": "chat_message",
                "sender_id": self.user_id,
                "recipient_id": recipient_id,
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "message_id": msg["message_id"]
            }
            
            sent = await self.p2p.send_message(recipient_id, message)
            if sent:
                await self.db.mark_message_sent(msg["message_id"])
    
    async def get_conversation(self, peer_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history with a specific peer"""
        return await self.db.get_conversation(self.user_id, peer_id, limit)
    
    def add_message_callback(self, callback):
        """Add callback for new messages"""
        self.message_callbacks.append(callback)
        