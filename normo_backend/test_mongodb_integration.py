#!/usr/bin/env python3
"""
Test script for MongoDB integration in Normo backend.
This script tests the hybrid storage system (MongoDB + JSON).
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from normo_backend.services.hybrid_storage import HybridConversationStorage
from normo_backend.models.schemas import ConversationMessage

def test_hybrid_storage():
    """Test the hybrid storage system."""
    print("🧪 Testing Hybrid Storage System")
    print("=" * 50)
    
    # Initialize hybrid storage
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/normo_db")
    storage = HybridConversationStorage(mongodb_url)
    
    # Test 1: Create a new conversation
    print("\n1. Creating a new conversation...")
    conversation_id = storage.create_conversation("test_user")
    print(f"✅ Created conversation: {conversation_id}")
    
    # Test 2: Add messages
    print("\n2. Adding messages...")
    
    # User message
    user_message = ConversationMessage(
        role="user",
        content="Test message for MongoDB integration",
        timestamp=datetime.now()
    )
    storage.add_message(conversation_id, user_message)
    print("✅ Added user message")
    
    # Assistant message
    assistant_message = ConversationMessage(
        role="assistant",
        content="This is a test response for MongoDB integration",
        timestamp=datetime.now(),
        agent_steps=["planner", "retriever", "summarizer"],
        pdf_names=["test_document.pdf"],
        source_citations=[{"pdf_name": "test_document.pdf", "page": 1}]
    )
    storage.add_message(conversation_id, assistant_message)
    print("✅ Added assistant message")
    
    # Test 3: Retrieve conversation
    print("\n3. Retrieving conversation...")
    conversation = storage.get_conversation(conversation_id)
    if conversation:
        print(f"✅ Retrieved conversation with {len(conversation.messages)} messages")
        print(f"   User ID: {conversation.user_id}")
        print(f"   Created: {conversation.created_at}")
        print(f"   Updated: {conversation.updated_at}")
    else:
        print("❌ Failed to retrieve conversation")
        return False
    
    # Test 4: List conversations
    print("\n4. Listing conversations...")
    conversations = storage.list_conversations("test_user")
    print(f"✅ Found {len(conversations)} conversations for test_user")
    
    # Test 5: Get conversation history
    print("\n5. Getting conversation history...")
    history = storage.get_conversation_history(conversation_id, limit=5)
    print(f"✅ Retrieved {len(history)} messages from history")
    
    # Test 6: Update context
    print("\n6. Updating conversation context...")
    context = {"test_key": "test_value", "timestamp": datetime.now().isoformat()}
    success = storage.update_conversation_context(conversation_id, context)
    if success:
        print("✅ Updated conversation context")
    else:
        print("❌ Failed to update conversation context")
    
    # Test 7: Get conversation summary
    print("\n7. Getting conversation summary...")
    summary = storage.get_conversation_summary(conversation_id)
    if summary:
        print(f"✅ Retrieved summary: {summary[:100]}...")
    else:
        print("ℹ️ No summary available (expected for test conversation)")
    
    # Cleanup
    storage.close()
    print("\n✅ All tests completed successfully!")
    return True

def test_api_endpoints():
    """Test the API endpoints."""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test 2: Create conversation via API
    print("\n2. Testing conversation creation via API...")
    try:
        response = requests.post(f"{base_url}/conversations")
        if response.status_code == 200:
            data = response.json()
            conversation_id = data["conversation_id"]
            print(f"✅ Created conversation via API: {conversation_id}")
        else:
            print(f"❌ Conversation creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False
    
    # Test 3: Send chat message
    print("\n3. Testing chat endpoint...")
    try:
        chat_data = {
            "messages": [
                {"role": "user", "content": "Test MongoDB integration via API"}
            ],
            "conversation_id": conversation_id
        }
        response = requests.post(f"{base_url}/chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat message sent successfully")
            print(f"   Response: {data['message']['content'][:100]}...")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return False
    
    # Test 4: List conversations
    print("\n4. Testing conversations list...")
    try:
        response = requests.get(f"{base_url}/conversations")
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Retrieved {len(conversations)} conversations")
        else:
            print(f"❌ Conversations list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations API error: {e}")
        return False
    
    # Test 5: Sync conversations
    print("\n5. Testing sync endpoint...")
    try:
        response = requests.post(f"{base_url}/sync-conversations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sync completed: {data['message']}")
        else:
            print(f"❌ Sync failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sync API error: {e}")
        return False
    
    print("\n✅ All API tests completed successfully!")
    return True

def main():
    """Main test function."""
    print("🚀 MongoDB Integration Test Suite")
    print("=" * 60)
    
    # Check if MongoDB URL is set
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("⚠️ MONGODB_URL not set, using default localhost URL")
        os.environ["MONGODB_URL"] = "mongodb://localhost:27017/normo_db"
    
    # Test hybrid storage
    storage_success = test_hybrid_storage()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Hybrid Storage: {'✅ PASS' if storage_success else '❌ FAIL'}")
    print(f"API Endpoints:  {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if storage_success and api_success:
        print("\n🎉 All tests passed! MongoDB integration is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    exit(main())
