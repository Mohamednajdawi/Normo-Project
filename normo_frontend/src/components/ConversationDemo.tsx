import React from 'react';
import { Box, Paper, Typography, Button, List, ListItem, ListItemText } from '@mui/material';
import { useConversation } from '../contexts/ConversationContext';
import { ConversationListItem } from '../types/api';

const ConversationDemo: React.FC = () => {
  const { state, createNewConversation, switchToConversation } = useConversation();
  const { conversations, currentConversationId } = state;

  const exampleQuestions = [
    "What are the building requirements in Austrian law?",
    "Can you tell me more about room height requirements?",
    "What about environmental regulations?",
    "How do I calculate playground area for apartments?",
  ];

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" sx={{ color: '#ffffff', mb: 2 }}>
        Conversation System Demo
      </Typography>
      
      <Paper sx={{ p: 2, mb: 2, bgcolor: '#444654' }}>
        <Typography variant="h6" sx={{ color: '#ffffff', mb: 1 }}>
          Current Status
        </Typography>
        <Typography variant="body2" sx={{ color: '#b4b4b4' }}>
          Current Conversation: {currentConversationId || 'None'}
        </Typography>
        <Typography variant="body2" sx={{ color: '#b4b4b4' }}>
          Total Conversations: {conversations.length}
        </Typography>
      </Paper>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          onClick={createNewConversation}
          sx={{ bgcolor: '#10a37f', '&:hover': { bgcolor: '#0d8c6c' } }}
        >
          Create New Conversation
        </Button>
      </Box>

      {conversations.length > 0 && (
        <Paper sx={{ p: 2, mb: 2, bgcolor: '#444654' }}>
          <Typography variant="h6" sx={{ color: '#ffffff', mb: 1 }}>
            Available Conversations
          </Typography>
          <List>
            {conversations.map((conversation) => (
              <ListItem
                key={conversation.conversation_id}
                onClick={() => switchToConversation(conversation.conversation_id)}
                sx={{
                  cursor: 'pointer',
                  bgcolor: conversation.conversation_id === currentConversationId 
                    ? 'rgba(16, 163, 127, 0.2)' 
                    : 'transparent',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': { bgcolor: 'rgba(16, 163, 127, 0.1)' },
                }}
              >
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ color: '#ffffff' }}>
                      {conversation.first_message.substring(0, 50) || 'New Conversation'}...
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" sx={{ color: '#b4b4b4' }}>
                      {conversation.message_count} messages • {new Date(conversation.updated_at).toLocaleString()}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Paper sx={{ p: 2, bgcolor: '#444654' }}>
        <Typography variant="h6" sx={{ color: '#ffffff', mb: 1 }}>
          Example Follow-up Questions
        </Typography>
        <Typography variant="body2" sx={{ color: '#b4b4b4', mb: 2 }}>
          Try these questions to test the conversation system:
        </Typography>
        <List>
          {exampleQuestions.map((question, index) => (
            <ListItem key={index} sx={{ py: 0.5 }}>
              <ListItemText
                primary={
                  <Typography variant="body2" sx={{ color: '#ffffff', fontStyle: 'italic' }}>
                    "{question}"
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default ConversationDemo;
