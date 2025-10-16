import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Public as CountryIcon,
  LocationOn as StateIcon,
  Business as BuildingIcon,
  Category as CategoryIcon,
  Description as DocumentIcon,
  Topic as SubjectIcon,
} from '@mui/icons-material';

interface MetadataSidebarProps {
  metadata?: Record<string, string> | null;
  isVisible: boolean;
}

const MetadataSidebar: React.FC<MetadataSidebarProps> = ({ metadata, isVisible }) => {
  if (!isVisible || !metadata) {
    return null;
  }

  const getDisplayValue = (key: string, value: string) => {
    if (!value || value === 'unknown' || value === '') {
      return 'Not specified';
    }
    return value;
  };

  const getChipColor = (value: string) => {
    if (!value || value === 'unknown' || value === '' || value === 'Not specified') {
      return 'default';
    }
    return 'primary';
  };

  const metadataItems = [
    {
      key: 'country',
      label: 'Country',
      icon: <CountryIcon />,
      value: getDisplayValue('country', metadata.country || ''),
      color: getChipColor(metadata.country || ''),
    },
    {
      key: 'state',
      label: 'State/Region',
      icon: <StateIcon />,
      value: getDisplayValue('state', metadata.state || ''),
      color: getChipColor(metadata.state || ''),
    },
    {
      key: 'legal_domain',
      label: 'Legal Domain',
      icon: <CategoryIcon />,
      value: getDisplayValue('legal_domain', metadata.legal_domain || ''),
      color: getChipColor(metadata.legal_domain || ''),
    },
    {
      key: 'document_type',
      label: 'Document Type',
      icon: <DocumentIcon />,
      value: getDisplayValue('document_type', metadata.document_type || ''),
      color: getChipColor(metadata.document_type || ''),
    },
    {
      key: 'subject_area',
      label: 'Subject Area',
      icon: <SubjectIcon />,
      value: getDisplayValue('subject_area', metadata.subject_area || ''),
      color: getChipColor(metadata.subject_area || ''),
    },
  ];

  // Add any custom metadata fields that might be in the response
  const customFields = Object.entries(metadata).filter(
    ([key]) => !['country', 'state', 'legal_domain', 'document_type', 'subject_area'].includes(key)
  );

  return (
    <Paper
      sx={{
        width: 300,
        height: '100vh',
        bgcolor: '#2d2d30',
        border: '1px solid #4d4d4f',
        borderRadius: 0,
        overflow: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ p: 2, borderBottom: '1px solid #4d4d4f' }}>
        <Typography
          variant="h6"
          sx={{
            color: '#10a37f',
            fontWeight: 600,
            textAlign: 'center',
            mb: 1,
          }}
        >
          Query Analysis
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#b4b4b4',
            textAlign: 'center',
            lineHeight: 1.4,
          }}
        >
          Extracted metadata from your legal query
        </Typography>
      </Box>

      <Box sx={{ flex: 1, p: 2 }}>
        <List sx={{ p: 0 }}>
          {metadataItems.map((item, index) => (
            <ListItem
              key={item.key}
              sx={{
                p: 1.5,
                mb: 1,
                borderRadius: 1,
                bgcolor: 'rgba(16, 163, 127, 0.05)',
                border: '1px solid #4d4d4f',
              }}
            >
              <ListItemIcon sx={{ color: '#10a37f', minWidth: 36 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="body2" sx={{ color: '#ffffff', fontWeight: 500, mb: 0.5 }}>
                    {item.label}
                  </Typography>
                }
                secondary={
                  <Chip
                    label={item.value}
                    size="small"
                    color={item.color as any}
                    sx={{
                      fontSize: '0.75rem',
                      height: 24,
                      '& .MuiChip-label': {
                        px: 1,
                      },
                    }}
                  />
                }
              />
            </ListItem>
          ))}
        </List>

        {customFields.length > 0 && (
          <>
            <Divider sx={{ bgcolor: '#4d4d4f', my: 2 }} />
            <Typography
              variant="subtitle2"
              sx={{
                color: '#10a37f',
                fontWeight: 600,
                mb: 2,
                textTransform: 'uppercase',
                fontSize: '0.75rem',
                letterSpacing: '0.5px',
              }}
            >
              Additional Fields
            </Typography>
            <List sx={{ p: 0 }}>
              {customFields.map(([key, value], index) => (
                <ListItem
                  key={key}
                  sx={{
                    p: 1.5,
                    mb: 1,
                    borderRadius: 1,
                    bgcolor: 'rgba(68, 70, 84, 0.3)',
                    border: '1px solid #4d4d4f',
                  }}
                >
                  <ListItemIcon sx={{ color: '#b4b4b4', minWidth: 36 }}>
                    <BuildingIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ color: '#ffffff', fontWeight: 500, mb: 0.5 }}>
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                    }
                    secondary={
                      <Chip
                        label={getDisplayValue(key, value)}
                        size="small"
                        color={getChipColor(value) as any}
                        sx={{
                          fontSize: '0.75rem',
                          height: 24,
                          '& .MuiChip-label': {
                            px: 1,
                          },
                        }}
                      />
                    }
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {/* Usage hint */}
        <Box sx={{ mt: 'auto', pt: 2 }}>
          <Paper
            sx={{
              p: 2,
              bgcolor: '#343541',
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
              This metadata helps our AI understand the legal context of your query and select the most relevant Austrian documents.
            </Typography>
          </Paper>
        </Box>
      </Box>
    </Paper>
  );
};

export default MetadataSidebar;
