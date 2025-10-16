# Frontend Conversation System

This document explains the conversation system implementation in the Normo frontend, which enables continuous conversations with context-aware responses.

## Overview

The frontend now supports:
- **Conversation Management**: Create, switch between, and persist conversations
- **Context-Aware Chat**: Follow-up questions that build upon previous context
- **Conversation History**: View and access previous conversations in the sidebar
- **State Persistence**: Conversations persist across browser sessions

## Key Components

### 1. ConversationContext (`contexts/ConversationContext.tsx`)

Central state management for conversations:

```typescript
const { state, createNewConversation, switchToConversation, sendMessage } = useConversation();
```

**State:**
- `currentConversationId`: ID of active conversation
- `conversations`: List of all conversations
- `messages`: Messages in current conversation
- `isLoading`: Loading state
- `error`: Error messages

**Methods:**
- `createNewConversation()`: Start a new conversation
- `switchToConversation(id)`: Switch to existing conversation
- `sendMessage(text)`: Send message to current conversation
- `loadConversations()`: Load all conversations from API

### 2. Updated API Service (`services/api.ts`)

New conversation-aware endpoints:

```typescript
// Send message with conversation context
chatApi.sendMessage(message, conversationId, userId)

// Create new conversation
chatApi.createConversation(userId)

// Get specific conversation
chatApi.getConversation(conversationId)

// List all conversations
chatApi.listConversations(userId)
```

### 3. Enhanced ChatInterface (`components/ChatInterface.tsx`)

- Uses conversation context for state management
- Shows conversation status in header
- Handles follow-up questions automatically
- Displays conversation ID for debugging

### 4. Updated Sidebar (`components/Sidebar.tsx`)

- Shows recent conversations (last 5)
- Click to switch between conversations
- Displays conversation titles and timestamps
- Shows message count for each conversation

## How It Works

### 1. Starting a New Conversation

```typescript
// User clicks "New Chat" button
const handleNewChat = async () => {
  await createNewConversation(); // Creates new conversation ID
  // Messages array is cleared
  // User can start fresh conversation
};
```

### 2. Sending Messages

```typescript
// First message - creates conversation
const response1 = await sendMessage("What are building requirements?");

// Follow-up message - uses existing conversation
const response2 = await sendMessage("Can you tell me more about room heights?");
```

### 3. Switching Conversations

```typescript
// User clicks on conversation in sidebar
const handleConversationClick = (conversationId) => {
  switchToConversation(conversationId); // Loads conversation messages
  // UI updates to show selected conversation
};
```

## User Experience

### Visual Indicators

1. **Header Status**: Shows if continuing conversation or starting new
2. **Conversation ID**: Displays current conversation ID (first 8 characters)
3. **Sidebar Highlighting**: Current conversation is highlighted
4. **Message Count**: Shows number of messages in each conversation

### Conversation Flow

1. **Initial Question**: User asks first question → New conversation created
2. **Follow-up Questions**: User asks follow-up → Uses existing conversation context
3. **Context Awareness**: AI responses reference previous conversation
4. **Persistence**: Conversations saved and restored across sessions

## State Persistence

### localStorage Integration

- Current conversation ID saved to localStorage
- Restored on page reload
- Automatically switches to last active conversation

### API Persistence

- All conversations stored on backend
- Messages include metadata (timestamps, citations, etc.)
- Conversations can be retrieved and resumed

## Example Usage

### Basic Conversation Flow

```typescript
// 1. User starts new conversation
await createNewConversation();

// 2. User asks initial question
await sendMessage("What are the building requirements in Austrian law?");

// 3. User asks follow-up question
await sendMessage("Can you tell me more about room height requirements?");

// 4. User switches to different conversation
await switchToConversation("different-conversation-id");
```

### Conversation Management

```typescript
// Load all conversations
await loadConversations();

// Get current conversation details
const currentConv = conversations.find(c => c.conversation_id === currentConversationId);

// Clear current conversation
clearCurrentConversation();
```

## Error Handling

- Network errors are caught and displayed
- Failed messages are removed from UI
- Conversation state is preserved on errors
- Fallback to legacy API if needed

## Development

### Adding New Features

1. **New Conversation Actions**: Add to ConversationContext
2. **UI Components**: Use `useConversation` hook
3. **API Integration**: Add methods to `chatApi`
4. **State Management**: Update reducer in ConversationContext

### Testing

```typescript
// Test conversation creation
const { createNewConversation } = useConversation();
await createNewConversation();
expect(state.currentConversationId).toBeTruthy();

// Test message sending
const { sendMessage } = useConversation();
await sendMessage("Test message");
expect(state.messages).toHaveLength(2); // User + Assistant
```

## Configuration

### Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
```

### Customization

- Conversation history limit (default: 5 in sidebar)
- Message count display
- Date formatting
- Conversation title truncation

## Troubleshooting

### Common Issues

1. **Conversation not persisting**: Check localStorage and API connectivity
2. **Messages not loading**: Verify conversation ID and API response
3. **Context not working**: Ensure conversation ID is passed to API
4. **UI not updating**: Check ConversationContext state updates

### Debug Information

- Conversation ID displayed in header
- Console logs for API calls
- Error messages in UI
- Network tab for API requests

## Future Enhancements

- Conversation search and filtering
- Message threading
- Conversation export/import
- Real-time collaboration
- Conversation analytics
- Message editing/deletion
