import React from 'react';
import { Box, Container } from '@mui/material';
import { ChatMessage } from '../types/api';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: ChatMessage[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <Box sx={{ flex: 1, py: 2 }}>
      <Container maxWidth="md">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </Container>
    </Box>
  );
};

export default MessageList;
