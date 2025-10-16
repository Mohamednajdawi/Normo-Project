import React, { useRef } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import { ConversationProvider } from './contexts/ConversationContext';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#10a37f',
    },
    background: {
      default: '#343541',
      paper: '#444654',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b4b4b4',
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", Roboto, sans-serif',
  },
});

function App() {
  const chatRef = useRef<{ handleNewChat: () => void }>(null);

  const handleNewChat = () => {
    chatRef.current?.handleNewChat();
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <ConversationProvider>
        <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
          <Sidebar onNewChat={handleNewChat} />
          <ChatInterface ref={chatRef} />
        </Box>
      </ConversationProvider>
    </ThemeProvider>
  );
}

export default App;