from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from normo_backend.models.schemas import Conversation, ConversationMessage
from normo_backend.services.conversation_storage import ConversationStorage
from normo_backend.services.mongodb_storage import MongoDBStorage


class HybridConversationStorage:
    """Hybrid conversation storage using both MongoDB and JSON files for redundancy."""
    
    def __init__(self, mongodb_url: Optional[str] = None, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize JSON storage (always available)
        self.json_storage = ConversationStorage(storage_dir)
        
        # Initialize MongoDB storage (if URL provided)
        self.mongodb_storage = None
        if mongodb_url:
            try:
                self.mongodb_storage = MongoDBStorage(mongodb_url, storage_dir)
                print("✅ MongoDB storage initialized successfully")
            except Exception as e:
                print(f"⚠️ MongoDB storage failed to initialize: {e}")
                print("📁 Falling back to JSON-only storage")
    
    def create_conversation(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        # Create in JSON storage first
        conversation_id = self.json_storage.create_conversation(user_id)
        
        # Also create in MongoDB if available
        if self.mongodb_storage:
            try:
                self.mongodb_storage.create_conversation(user_id)
            except Exception as e:
                print(f"⚠️ Failed to create conversation in MongoDB: {e}")
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID. Try MongoDB first, then JSON."""
        # Try MongoDB first if available
        if self.mongodb_storage:
            try:
                conversation = self.mongodb_storage.get_conversation(conversation_id)
                if conversation:
                    return conversation
            except Exception as e:
                print(f"⚠️ Failed to get conversation from MongoDB: {e}")
        
        # Fallback to JSON storage
        return self.json_storage.get_conversation(conversation_id)
    
    def add_message(self, conversation_id: str, message: ConversationMessage) -> bool:
        """Add a message to a conversation."""
        success = False
        
        # Add to JSON storage
        if self.json_storage.add_message(conversation_id, message):
            success = True
        
        # Also add to MongoDB if available
        if self.mongodb_storage:
            try:
                self.mongodb_storage.add_message(conversation_id, message)
            except Exception as e:
                print(f"⚠️ Failed to add message to MongoDB: {e}")
        
        return success
    
    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for context."""
        # Try MongoDB first if available
        if self.mongodb_storage:
            try:
                history = self.mongodb_storage.get_conversation_history(conversation_id, limit)
                if history:
                    return history
            except Exception as e:
                print(f"⚠️ Failed to get conversation history from MongoDB: {e}")
        
        # Fallback to JSON storage
        return self.json_storage.get_conversation_history(conversation_id, limit)
    
    def update_conversation_context(self, conversation_id: str, context: Dict) -> bool:
        """Update conversation context."""
        success = False
        
        # Update JSON storage
        if self.json_storage.update_conversation_context(conversation_id, context):
            success = True
        
        # Also update MongoDB if available
        if self.mongodb_storage:
            try:
                self.mongodb_storage.update_conversation_context(conversation_id, context)
            except Exception as e:
                print(f"⚠️ Failed to update conversation context in MongoDB: {e}")
        
        return success
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Get a summary of the conversation for context."""
        # Try MongoDB first if available
        if self.mongodb_storage:
            try:
                summary = self.mongodb_storage.get_conversation_summary(conversation_id)
                if summary:
                    return summary
            except Exception as e:
                print(f"⚠️ Failed to get conversation summary from MongoDB: {e}")
        
        # Fallback to JSON storage
        return self.json_storage.get_conversation_summary(conversation_id)
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[Dict]:
        """List conversations for a user."""
        # Try MongoDB first if available
        if self.mongodb_storage:
            try:
                conversations = self.mongodb_storage.list_conversations(user_id)
                if conversations:
                    return conversations
            except Exception as e:
                print(f"⚠️ Failed to list conversations from MongoDB: {e}")
        
        # Fallback to JSON storage
        return self.json_storage.list_conversations(user_id)
    
    def sync_from_json_to_mongodb(self):
        """Sync all conversations from JSON files to MongoDB."""
        if not self.mongodb_storage:
            print("❌ MongoDB storage not available for sync")
            return
        
        print("🔄 Syncing conversations from JSON to MongoDB...")
        synced_count = 0
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    conversation = Conversation(**data)
                    
                    # Save to MongoDB
                    self.mongodb_storage._save_conversation_to_mongodb(conversation)
                    synced_count += 1
                    
            except Exception as e:
                print(f"⚠️ Failed to sync {file_path}: {e}")
        
        print(f"✅ Synced {synced_count} conversations to MongoDB")
    
    def close(self):
        """Close all storage connections."""
        if self.mongodb_storage:
            self.mongodb_storage.close()
