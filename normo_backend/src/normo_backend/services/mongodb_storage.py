from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from normo_backend.models.schemas import Conversation, ConversationMessage


class MongoDBStorage:
    """MongoDB-based conversation storage with JSON backup."""
    
    def __init__(self, mongodb_url: str, storage_dir: str = "conversations"):
        self.mongodb_url = mongodb_url
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize MongoDB client
        self.client = MongoClient(mongodb_url)
        self.db = self.client.normo_db
        self.conversations_collection = self.db.conversations
        self.messages_collection = self.db.messages
        
        # In-memory cache for quick access
        self._conversations: Dict[str, Conversation] = {}
        self._load_conversations_from_mongodb()
    
    def _load_conversations_from_mongodb(self):
        """Load conversations from MongoDB into memory cache."""
        try:
            for doc in self.conversations_collection.find():
                # Convert MongoDB document to Conversation object
                conversation = Conversation(
                    conversation_id=doc['conversation_id'],
                    user_id=doc.get('user_id'),
                    messages=[],
                    created_at=doc['created_at'],
                    updated_at=doc['updated_at'],
                    context=doc.get('context', {})
                )
                
                # Load messages for this conversation
                messages = list(self.messages_collection.find(
                    {'conversation_id': conversation.conversation_id}
                ).sort('timestamp', 1))
                
                for msg_doc in messages:
                    message = ConversationMessage(
                        role=msg_doc['role'],
                        content=msg_doc['content'],
                        timestamp=msg_doc['timestamp'],
                        agent_steps=msg_doc.get('agent_steps'),
                        pdf_names=msg_doc.get('pdf_names'),
                        source_citations=msg_doc.get('source_citations'),
                        meta_data=msg_doc.get('meta_data')
                    )
                    conversation.messages.append(message)
                
                self._conversations[conversation.conversation_id] = conversation
                
        except Exception as e:
            print(f"Error loading conversations from MongoDB: {e}")
    
    def _save_conversation_to_mongodb(self, conversation: Conversation):
        """Save a conversation to MongoDB."""
        try:
            # Save conversation metadata
            conversation_doc = {
                'conversation_id': conversation.conversation_id,
                'user_id': conversation.user_id,
                'created_at': conversation.created_at,
                'updated_at': conversation.updated_at,
                'context': conversation.context
            }
            
            self.conversations_collection.replace_one(
                {'conversation_id': conversation.conversation_id},
                conversation_doc,
                upsert=True
            )
            
            # Save messages
            self.messages_collection.delete_many(
                {'conversation_id': conversation.conversation_id}
            )
            
            for message in conversation.messages:
                message_doc = {
                    'conversation_id': conversation.conversation_id,
                    'role': message.role,
                    'content': message.content,
                    'timestamp': message.timestamp,
                    'agent_steps': message.agent_steps,
                    'pdf_names': message.pdf_names,
                    'source_citations': message.source_citations,
                    'meta_data': message.meta_data
                }
                self.messages_collection.insert_one(message_doc)
                
        except Exception as e:
            print(f"Error saving conversation to MongoDB: {e}")
    
    def _save_conversation_to_json(self, conversation: Conversation):
        """Save a conversation to JSON file as backup."""
        file_path = self.storage_dir / f"{conversation.conversation_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use model_dump() for Pydantic v2, fallback to dict() for v1
                try:
                    conversation_data = conversation.model_dump()
                except AttributeError:
                    conversation_data = conversation.dict()
                json.dump(conversation_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving conversation to JSON: {e}")
    
    def create_conversation(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._conversations[conversation_id] = conversation
        self._save_conversation_to_mongodb(conversation)
        self._save_conversation_to_json(conversation)
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)
    
    def add_message(self, conversation_id: str, message: ConversationMessage) -> bool:
        """Add a message to a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        self._save_conversation_to_mongodb(conversation)
        self._save_conversation_to_json(conversation)
        return True
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []
        
        # Get the last 'limit' messages
        recent_messages = conversation.messages[-limit:] if len(conversation.messages) > limit else conversation.messages
        
        # Convert to dict format for agent context
        history = []
        for msg in recent_messages:
            history.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "agent_steps": msg.agent_steps,
                "pdf_names": msg.pdf_names,
                "source_citations": msg.source_citations,
                "meta_data": msg.meta_data
            })
        
        return history
    
    def update_conversation_context(self, conversation_id: str, context: Dict) -> bool:
        """Update conversation context."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False
        
        conversation.context.update(context)
        conversation.updated_at = datetime.now()
        self._save_conversation_to_mongodb(conversation)
        self._save_conversation_to_json(conversation)
        return True
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Get a summary of the conversation for context."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or not conversation.messages:
            return None
        
        # Find the last assistant message with a summary
        for msg in reversed(conversation.messages):
            if msg.role == "assistant" and msg.agent_steps and "summarizer" in msg.agent_steps:
                return msg.content
        
        return None
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[Dict]:
        """List conversations for a user."""
        conversations = []
        for conv in self._conversations.values():
            if user_id is None or conv.user_id == user_id:
                # Get the first user message for the title
                first_user_message = None
                for msg in conv.messages:
                    if msg.role == "user":
                        first_user_message = msg
                        break
                
                conversations.append({
                    "conversation_id": conv.conversation_id,
                    "user_id": conv.user_id,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages),
                    "first_message": first_user_message.content if first_user_message else "New Conversation"
                })
        
        # Sort by updated_at descending
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
