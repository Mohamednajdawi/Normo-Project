# Conversation System Documentation

This document explains the conversation storage and follow-up question system implemented in the Normo backend.

## Overview

The conversation system allows users to have continuous conversations with the AI agent, where follow-up questions can build upon previous context. The system stores conversation history and uses it to provide context-aware responses.

## Key Features

- **Conversation Persistence**: Conversations are stored in JSON files and persist between sessions
- **Follow-up Questions**: Users can ask follow-up questions that reference previous context
- **Context-Aware Responses**: The AI agent uses conversation history to provide more relevant answers
- **Source Citations**: Each response includes citations to the relevant documents used

## API Endpoints

### Create a New Conversation
```http
POST /conversations
Content-Type: application/json

{
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "conversation_id": "uuid-string"
}
```

### Send a Message
```http
POST /chat
Content-Type: application/json

{
  "messages": [
    {
      "role": "user",
      "content": "What are the building requirements in Austrian law?"
    }
  ],
  "conversation_id": "uuid-string",  // Optional for new conversations
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "Based on your request about building requirements...",
    "timestamp": "2024-01-01T12:00:00"
  },
  "conversation_id": "uuid-string",
  "source_citations": [
    {
      "document": "Bauordnung_1994.pdf",
      "page": 15,
      "content": "Room heights must be at least 2.5m..."
    }
  ]
}
```

### Get a Conversation
```http
GET /conversations/{conversation_id}
```

### List Conversations
```http
GET /conversations?user_id=optional_user_id
```

## Data Models

### ConversationMessage
```python
class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    agent_steps: Optional[List[str]] = None
    pdf_names: Optional[List[str]] = None
    source_citations: Optional[List[Dict]] = None
    meta_data: Optional[Dict] = None
```

### Conversation
```python
class Conversation(BaseModel):
    conversation_id: str
    user_id: Optional[str] = None
    messages: List[ConversationMessage] = []
    created_at: datetime
    updated_at: datetime
    context: Dict = {}  # Additional context storage
```

## How Follow-up Questions Work

1. **Initial Question**: User asks a question, system creates a new conversation
2. **Context Storage**: System stores the user's question and the AI's response with metadata
3. **Follow-up Question**: User asks a follow-up question using the same conversation_id
4. **Context Retrieval**: System retrieves recent conversation history (last 5 messages)
5. **Context-Aware Processing**: AI agents use conversation history to provide better responses
6. **Response Storage**: New response is stored in the conversation

## Example Usage

### Python Example
```python
import requests

# Create conversation
response = requests.post("http://localhost:8000/conversations")
conversation_id = response.json()["conversation_id"]

# Send initial message
response = requests.post("http://localhost:8000/chat", json={
    "messages": [{"role": "user", "content": "What are building requirements?"}],
    "conversation_id": conversation_id
})

# Send follow-up question
response = requests.post("http://localhost:8000/chat", json={
    "messages": [{"role": "user", "content": "Can you tell me more about room heights?"}],
    "conversation_id": conversation_id
})
```

### JavaScript Example
```javascript
// Create conversation
const createResponse = await fetch('http://localhost:8000/conversations', {
  method: 'POST'
});
const { conversation_id } = await createResponse.json();

// Send initial message
const chatResponse = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'What are building requirements?' }],
    conversation_id: conversation_id
  })
});

// Send follow-up question
const followUpResponse = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Can you tell me more about room heights?' }],
    conversation_id: conversation_id
  })
});
```

## Storage

Conversations are stored in the `conversations/` directory as JSON files. Each conversation is stored as `{conversation_id}.json`.

## Configuration

The conversation storage can be configured by modifying the `ConversationStorage` class in `services/conversation_storage.py`:

```python
# Change storage directory
storage = ConversationStorage(storage_dir="custom_conversations")

# Change history limit for context
history = storage.get_conversation_history(conversation_id, limit=10)
```

## Testing

Test the conversation system by using the API endpoints directly or through the frontend interface.

Make sure the backend is running on `http://localhost:8000`.

## Error Handling

- Invalid conversation IDs return 404 errors
- Missing messages return 400 errors
- Storage errors are logged but don't break the API
- Fallback responses are provided if JSON parsing fails

## Future Enhancements

- Database integration (PostgreSQL, MongoDB)
- Conversation search and filtering
- Message threading
- Conversation analytics
- Export/import functionality
