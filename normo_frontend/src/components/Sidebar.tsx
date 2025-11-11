import React from 'react';
import {
  Box,
  Drawer,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Add as AddIcon,
  Architecture as ArchitectureIcon,
  Gavel as GavelIcon,
  Calculate as CalculateIcon,
  Description as DescriptionIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useConversation } from '../contexts/ConversationContext';
import { ConversationListItem } from '../types/api';
import { useTranslation } from '../i18n/useTranslation';

const SIDEBAR_WIDTH = 260;

interface SidebarProps {
  onNewChat?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat }) => {
  const { state, switchToConversation } = useConversation();
  const { conversations, currentConversationId } = state;
  const { t } = useTranslation();

  const features = [
    {
      icon: <ArchitectureIcon />,
      title: t('featureBuildingCodes'),
      description: t('featureBuildingCodesDesc'),
    },
    {
      icon: <CalculateIcon />,
      title: t('featureAreaCalculations'),
      description: t('featureAreaCalculationsDesc'),
    },
    {
      icon: <GavelIcon />,
      title: t('featureLegalCitations'),
      description: t('featureLegalCitationsDesc'),
    },
    {
      icon: <DescriptionIcon />,
      title: t('featurePdfDocuments'),
      description: t('featurePdfDocumentsDesc'),
    },
  ];

  const formatConversationTitle = (conversation: ConversationListItem) => {
    if (!conversation) {
      return t('newConversation');
    }
    
    // Use first_message from the list view
    const firstMessage = conversation.first_message;
    
    if (firstMessage) {
      return firstMessage.length > 50 
        ? firstMessage.substring(0, 50) + '...'
        : firstMessage;
    }
    return t('newConversation');
  };

  const formatDate = (dateString: string) => {
    if (!dateString) {
      return t('unknown');
    }
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return t('unknown');
      }
      
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
      
      if (diffInHours < 24) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else if (diffInHours < 168) { // 7 days
        return date.toLocaleDateString([], { weekday: 'short' });
      } else {
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
    } catch (error) {
      return t('unknown');
    }
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: SIDEBAR_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: SIDEBAR_WIDTH,
          boxSizing: 'border-box',
          bgcolor: '#202123',
          borderRight: '1px solid #4d4d4f',
        },
      }}
    >
      <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={onNewChat}
          sx={{
            mb: 2,
            borderColor: '#4d4d4f',
            color: '#ffffff',
            textTransform: 'none',
            justifyContent: 'flex-start',
            '&:hover': {
              borderColor: '#10a37f',
              bgcolor: 'rgba(16, 163, 127, 0.1)',
            },
          }}
          fullWidth
        >
          {t('newChat')}
        </Button>

        {/* Logo */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <Avatar
            src="/logo.jpg"
            alt="Normo Logo"
            sx={{
              width: 80,
              height: 80,
              borderRadius: 2,
              bgcolor: 'transparent',
            }}
            variant="rounded"
          />
        </Box>

        {/* Title */}
        <Typography
          variant="h6"
          sx={{
            mb: 2,
            color: '#ffffff',
            fontWeight: 600,
            textAlign: 'center',
          }}
        >
          {t('sidebarTitle')}
        </Typography>

        <Typography
          variant="body2"
          sx={{
            mb: 3,
            color: '#b4b4b4',
            textAlign: 'center',
            lineHeight: 1.4,
          }}
        >
          {t('sidebarDescription')}
        </Typography>

        <Divider sx={{ bgcolor: '#4d4d4f', mb: 2 }} />

        {/* Recent Conversations */}
        {conversations.length > 0 && (
          <>
            <Typography
              variant="subtitle2"
              sx={{
                mb: 2,
                color: '#10a37f',
                fontWeight: 600,
                textTransform: 'uppercase',
                fontSize: '0.75rem',
                letterSpacing: '0.5px',
              }}
            >
              {t('recentConversations')}
            </Typography>

            <List sx={{ p: 0, mb: 2 }}>
              {(conversations || []).slice(0, 5).map((conversation) => (
                <ListItem
                  key={conversation.conversation_id}
                  onClick={() => switchToConversation(conversation.conversation_id)}
                  sx={{
                    p: 1,
                    mb: 1,
                    borderRadius: 1,
                    cursor: 'pointer',
                    bgcolor: conversation.conversation_id === currentConversationId 
                      ? 'rgba(16, 163, 127, 0.2)' 
                      : 'transparent',
                    border: conversation.conversation_id === currentConversationId 
                      ? '1px solid #10a37f' 
                      : '1px solid transparent',
                    '&:hover': {
                      bgcolor: conversation.conversation_id === currentConversationId 
                        ? 'rgba(16, 163, 127, 0.3)' 
                        : 'rgba(16, 163, 127, 0.1)',
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: '#10a37f', minWidth: 36 }}>
                    <ChatIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#ffffff', 
                          fontWeight: 500,
                          fontSize: '0.8rem',
                          lineHeight: 1.3,
                        }}
                      >
                        {formatConversationTitle(conversation)}
                      </Typography>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Typography variant="caption" sx={{ color: '#b4b4b4' }}>
                          {formatDate(conversation.updated_at)}
                        </Typography>
                        <Chip
                          label={`${conversation.message_count || 0} ${t('msgs')}`}
                          size="small"
                          sx={{
                            height: 16,
                            fontSize: '0.65rem',
                            bgcolor: '#4d4d4f',
                            color: '#b4b4b4',
                            '& .MuiChip-label': {
                              px: 0.5,
                            },
                          }}
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Divider sx={{ bgcolor: '#4d4d4f', mb: 2 }} />
          </>
        )}

        {/* Features */}
        <Typography
          variant="subtitle2"
          sx={{
            mb: 2,
            color: '#10a37f',
            fontWeight: 600,
            textTransform: 'uppercase',
            fontSize: '0.75rem',
            letterSpacing: '0.5px',
          }}
        >
          {t('features')}
        </Typography>

        <List sx={{ p: 0 }}>
          {features.map((feature, index) => (
            <ListItem
              key={index}
              sx={{
                p: 1,
                mb: 1,
                borderRadius: 1,
                '&:hover': {
                  bgcolor: 'rgba(16, 163, 127, 0.1)',
                },
              }}
            >
              <ListItemIcon sx={{ color: '#10a37f', minWidth: 36 }}>
                {feature.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="body2" sx={{ color: '#ffffff', fontWeight: 500 }}>
                    {feature.title}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" sx={{ color: '#b4b4b4' }}>
                    {feature.description}
                  </Typography>
                }
              />
            </ListItem>
          ))}
        </List>

        {/* Bottom Info */}
        <Box sx={{ mt: 'auto', pt: 2 }}>
          <Paper
            sx={{
              p: 2,
              bgcolor: '#2d2d30',
              border: '1px solid #4d4d4f',
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: '#b4b4b4',
                display: 'block',
                textAlign: 'center',
                lineHeight: 1.4,
              }}
            >
              {t('askQuestionsPrompt')}
            </Typography>
          </Paper>
        </Box>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
