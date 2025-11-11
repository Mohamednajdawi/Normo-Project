import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Chip,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Person as PersonIcon,
  SmartToy as BotIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Description as DocumentIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage } from '../types/api';
import CitationsList from './CitationsList';
import { useTranslation } from '../i18n/useTranslation';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showCitations, setShowCitations] = useState(false);
  const isUser = message.role === 'user';
  const hasCitations = message.citations && message.citations.length > 0;
  const { t } = useTranslation();

  return (
    <Box
      sx={{
        mb: 3,
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      {/* Message Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          mb: 1,
          gap: 1,
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        <Avatar
          sx={{
            bgcolor: isUser ? '#10a37f' : '#444654',
            width: 32,
            height: 32,
          }}
        >
          {isUser ? <PersonIcon /> : <BotIcon />}
        </Avatar>
        <Typography
          variant="caption"
          sx={{
            color: '#b4b4b4',
            fontWeight: 500,
          }}
        >
          {isUser ? t('you') : t('assistant')}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            color: '#8e8ea0',
            ml: 1,
          }}
        >
          {message.timestamp.toLocaleTimeString()}
        </Typography>
      </Box>

      {/* Message Content */}
      <Paper
        sx={{
          p: 2,
          maxWidth: '80%',
          bgcolor: isUser ? '#10a37f' : '#444654',
          color: '#ffffff',
          borderRadius: 2,
          '& pre': {
            bgcolor: '#2d2d30',
            p: 1,
            borderRadius: 1,
            overflow: 'auto',
          },
          '& code': {
            bgcolor: '#2d2d30',
            px: 0.5,
            py: 0.25,
            borderRadius: 0.5,
            fontSize: '0.875rem',
          },
          '& blockquote': {
            borderLeft: '3px solid #10a37f',
            pl: 2,
            ml: 0,
            fontStyle: 'italic',
          },
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            p: ({ children }) => (
              <Typography variant="body1" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>
                {children}
              </Typography>
            ),
            h1: ({ children }) => (
              <Typography variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
                {children}
              </Typography>
            ),
            h2: ({ children }) => (
              <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                {children}
              </Typography>
            ),
            h3: ({ children }) => (
              <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                {children}
              </Typography>
            ),
            li: ({ children }) => (
              <Typography component="li" variant="body1" sx={{ mb: 0.5 }}>
                {children}
              </Typography>
            ),
            strong: ({ children }) => (
              <Typography component="span" sx={{ fontWeight: 700, color: '#10a37f' }}>
                {children}
              </Typography>
            ),
          }}
        >
          {message.content}
        </ReactMarkdown>
      </Paper>

      {/* Citations Section */}
      {hasCitations && (
        <Box sx={{ mt: 2, width: '100%', maxWidth: '80%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Chip
              icon={<DocumentIcon />}
              label={`${message.citations!.length} ${message.citations!.length > 1 ? t('sources') : t('source')}`}
              size="small"
              sx={{
                bgcolor: '#2d2d30',
                color: '#10a37f',
                '& .MuiChip-icon': { color: '#10a37f' },
              }}
            />
            {message.citations!.some(c => c.calculations || c.area_measurements) && (
              <Chip
                icon={<CalculateIcon />}
                label={t('containsCalculations')}
                size="small"
                sx={{
                  ml: 1,
                  bgcolor: '#2d2d30',
                  color: '#ff9800',
                  '& .MuiChip-icon': { color: '#ff9800' },
                }}
              />
            )}
            <IconButton
              size="small"
              onClick={() => setShowCitations(!showCitations)}
              sx={{ ml: 'auto', color: '#10a37f' }}
            >
              {showCitations ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={showCitations}>
            <Paper
              sx={{
                bgcolor: '#2d2d30',
                border: '1px solid #4d4d4f',
              }}
            >
              <CitationsList citations={message.citations!} />
            </Paper>
          </Collapse>
        </Box>
      )}
    </Box>
  );
};

export default MessageBubble;
