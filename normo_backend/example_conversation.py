#!/usr/bin/env python3
"""
Example script demonstrating the conversation storage system.
This shows how to use the new conversation-aware API endpoints.
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def create_conversation(user_id: str = None) -> str:
    """Create a new conversation."""
    response = requests.post(f"{BASE_URL}/conversations", params={"user_id": user_id})
    response.raise_for_status()
    return response.json()["conversation_id"]

def send_message(conversation_id: str, message: str, user_id: str = None) -> Dict[str, Any]:
    """Send a message to a conversation."""
    payload = {
        "messages": [{"role": "user", "content": message}],
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    response.raise_for_status()
    return response.json()

def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """Get a conversation by ID."""
    response = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
    response.raise_for_status()
    return response.json()

def list_conversations(user_id: str = None) -> list:
    """List conversations for a user."""
    response = requests.get(f"{BASE_URL}/conversations", params={"user_id": user_id})
    response.raise_for_status()
    return response.json()

def main():
    """Demonstrate the conversation system."""
    print("=== Normo Conversation System Demo ===\n")
    
    # Create a new conversation
    print("1. Creating a new conversation...")
    conversation_id = create_conversation(user_id="demo_user")
    print(f"   Conversation ID: {conversation_id}\n")
    
    # Send initial message
    print("2. Sending initial message...")
    initial_message = "What are the building requirements in Austrian law?"
    print(f"   User: {initial_message}")
    
    response1 = send_message(conversation_id, initial_message, user_id="demo_user")
    print(f"   Assistant: {response1['message']['content']}")
    print(f"   Source Citations: {len(response1.get('source_citations', []))} sources found\n")
    
    # Send follow-up question
    print("3. Sending follow-up question...")
    follow_up = "Can you tell me more about the room height requirements?"
    print(f"   User: {follow_up}")
    
    response2 = send_message(conversation_id, follow_up, user_id="demo_user")
    print(f"   Assistant: {response2['message']['content']}")
    print(f"   Source Citations: {len(response2.get('source_citations', []))} sources found\n")
    
    # Send another follow-up
    print("4. Sending another follow-up question...")
    follow_up2 = "What about environmental regulations?"
    print(f"   User: {follow_up2}")
    
    response3 = send_message(conversation_id, follow_up2, user_id="demo_user")
    print(f"   Assistant: {response3['message']['content']}")
    print(f"   Source Citations: {len(response3.get('source_citations', []))} sources found\n")
    
    # Get full conversation
    print("5. Retrieving full conversation...")
    conversation = get_conversation(conversation_id)
    print(f"   Total messages: {len(conversation['messages'])}")
    print(f"   Created: {conversation['created_at']}")
    print(f"   Updated: {conversation['updated_at']}\n")
    
    # List all conversations
    print("6. Listing all conversations...")
    conversations = list_conversations(user_id="demo_user")
    print(f"   Found {len(conversations)} conversations:")
    for conv in conversations:
        print(f"   - {conv['conversation_id']}: {conv['message_count']} messages")
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
