import asyncio
import asyncpg
from typing import Dict, List, Optional
import datetime
import json

class DatabaseManager:
    """Manages database operations for the chat application"""
    
    def __init__(self, dsn: str):
        """Initialize with connection string"""
        self.dsn = dsn
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection and tables"""
        self.pool = await asyncpg.create_pool(self.dsn)
        
        async with self.pool.acquire() as conn:
            # Create tables if they don't exist
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    last_seen TIMESTAMP NOT NULL
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
                    is_delivered BOOLEAN NOT NULL DEFAULT FALSE
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS pending_messages (
                    message_id TEXT PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (message_id) REFERENCES messages(message_id)
                )
            ''')
    
    async def register_user(self, user_id: str, username: str):
        """Register a user in the database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                INSERT INTO users (user_id, username, last_seen)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) 
                DO UPDATE SET username = $2, last_seen = $3
                ''',
                user_id,
                username,
                datetime.datetime.now()
            )
    
    async def update_last_seen(self, user_id: str):
        """Update user's last seen timestamp"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                UPDATE users SET last_seen = $1 WHERE user_id = $2
                ''',
                datetime.datetime.now(),
                user_id
            )
    
    async def store_message(self, message_id: str, sender_id: str, 
                          recipient_id: str, content: str, 
                          timestamp: str, is_sent: bool):
        """Store a message in the database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                INSERT INTO messages 
                (message_id, sender_id, recipient_id, content, timestamp, is_sent)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (message_id) 
                DO UPDATE SET is_sent = $6
                ''',
                message_id,
                sender_id,
                recipient_id,
                content,
                datetime.datetime.fromisoformat(timestamp),
                is_sent
            )
    
    async def store_pending_message(self, message_id: str, sender_id: str, 
                                  recipient_id: str, content: str, timestamp: str):
        """Store a pending message to be sent later"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                INSERT INTO pending_messages 
                (message_id, sender_id, recipient_id, content, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (message_id) DO NOTHING
                ''',
                message_id,
                sender_id,
                recipient_id,
                content,
                datetime.datetime.fromisoformat(timestamp)
            )
    
    async def mark_message_sent(self, message_id: str):
        """Mark a message as sent and remove from pending"""
        async with self.pool.acquire() as conn:
            # Start a transaction
            async with conn.transaction():
                # Update message status
                await conn.execute(
                    '''
                    UPDATE messages SET is_sent = TRUE
                    WHERE message_id = $1
                    ''',
                    message_id
                )
                
                # Remove from pending
                await conn.execute(
                    '''
                    DELETE FROM pending_messages
                    WHERE message_id = $1
                    ''',
                    message_id
                )
    
    async def mark_message_delivered(self, message_id: str):
        """Mark a message as delivered"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                UPDATE messages SET is_delivered = TRUE
                WHERE message_id = $1
                ''',
                message_id
            )
    
    async def get_pending_messages(self, recipient_id: str) -> List[Dict]:
        """Get all pending messages for a recipient"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                '''
                SELECT * FROM pending_messages
                WHERE recipient_id = $1
                ORDER BY timestamp ASC
                ''',
                recipient_id
            )
            return [dict(row) for row in rows]
    
    async def get_conversation(self, user_id: str, peer_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history with a specific peer"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                '''
                SELECT * FROM messages
                WHERE (sender_id = $1 AND recipient_id = $2)
                OR (sender_id = $2 AND recipient_id = $1)
                ORDER BY timestamp DESC
                LIMIT $3
                ''',
                user_id,
                peer_id,
                limit
            )
            return [dict(row) for row in rows]