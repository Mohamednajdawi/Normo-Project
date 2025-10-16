import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Calculate as CalculateIcon,
  StraightenOutlined as RulerIcon,
  PageviewOutlined as PageIcon,
} from '@mui/icons-material';
import { SourceCitation } from '../types/api';

interface CitationsListProps {
  citations: SourceCitation[];
}

const extractDocumentName = (pdfName: string): string => {
  // Remove .pdf extension
  let name = pdfName.replace('.pdf', '');
  
  // Extract the meaningful part of the filename
  // For hierarchical paths, get the filename without the path
  const filename = name.split('/').pop() || name;
  
  // Remove the prefix pattern (e.g., "1_AT_OOE_0_GE_" or "3_AT_0_0_OIB_")
  // and keep the descriptive title
  const parts = filename.split('_');
  
  // Find the start of the descriptive title (usually after the pattern)
  let titleStart = 0;
  for (let i = 0; i < parts.length; i++) {
    // Look for patterns like "GE_", "VE_", "OIB_", "OEN_"
    if (['GE', 'VE', 'OIB', 'OEN'].includes(parts[i])) {
      titleStart = i + 1;
      break;
    }
  }
  
  // If we found a pattern, extract the title part
  if (titleStart > 0 && titleStart < parts.length) {
    const titleParts = parts.slice(titleStart);
    // Remove year at the end if it exists (4 digits)
    if (titleParts.length > 0 && /^\d{4}$/.test(titleParts[titleParts.length - 1])) {
      titleParts.pop();
    }
    return titleParts.join(' ').replace(/_/g, ' ');
  }
  
  // Fallback: return the filename with underscores replaced by spaces
  return filename.replace(/_/g, ' ');
};

const openPdfInNewWindow = (pdfName: string): void => {
  // Get the API base URL from environment or use default
  const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  // Construct the PDF URL
  const pdfUrl = `${apiBaseUrl}/pdf/${encodeURIComponent(pdfName)}`;
  
  // Open PDF in new window/tab
  window.open(pdfUrl, '_blank', 'noopener,noreferrer');
};

const CitationsList: React.FC<CitationsListProps> = ({ citations }) => {
  return (
    <Box sx={{ p: 2 }}>
      <Typography
        variant="subtitle2"
        sx={{
          color: '#10a37f',
          fontWeight: 600,
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <DocumentIcon fontSize="small" />
        Legal Sources & Citations
      </Typography>

      <List sx={{ p: 0 }}>
        {citations.map((citation, index) => (
          <Box key={index}>
            <ListItem
              sx={{
                p: 2,
                flexDirection: 'column',
                alignItems: 'flex-start',
                bgcolor: index % 2 === 0 ? '#343541' : 'transparent',
                borderRadius: 1,
              }}
            >
              {/* Citation Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, width: '100%' }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <DocumentIcon sx={{ color: '#10a37f' }} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#10a37f',
                        fontWeight: 600,
                        wordBreak: 'break-word',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        '&:hover': {
                          color: '#0d8a6b',
                          textDecoration: 'underline',
                        },
                      }}
                      onClick={() => openPdfInNewWindow(citation.pdf_name)}
                    >
                      {extractDocumentName(citation.pdf_name)}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                      <Chip
                        icon={<PageIcon />}
                        label={`Page ${citation.page}`}
                        size="small"
                        sx={{
                          bgcolor: '#10a37f',
                          color: '#ffffff',
                          '& .MuiChip-icon': { color: '#ffffff' },
                          fontSize: '0.75rem',
                        }}
                      />
                      <Chip
                        label={`Section ${citation.paragraph}`}
                        size="small"
                        sx={{
                          bgcolor: '#444654',
                          color: '#ffffff',
                          fontSize: '0.75rem',
                        }}
                      />
                    </Box>
                  }
                />
              </Box>

              {/* Content Preview */}
              <Typography
                variant="body2"
                sx={{
                  color: '#b4b4b4',
                  mb: 2,
                  lineHeight: 1.5,
                  fontStyle: 'italic',
                  pl: 5,
                }}
              >
                "{citation.relevant_content}"
              </Typography>

              {/* Calculations and Measurements */}
              {(citation.calculations || citation.area_measurements) && (
                <Box sx={{ pl: 5, width: '100%' }}>
                  {citation.calculations && citation.calculations.length > 0 && (
                    <Box sx={{ mb: 1 }}>
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#ff9800',
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          mb: 0.5,
                        }}
                      >
                        <CalculateIcon fontSize="small" />
                        Calculations Found:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {citation.calculations.map((calc, calcIndex) => (
                          <Chip
                            key={calcIndex}
                            label={calc}
                            size="small"
                            sx={{
                              bgcolor: '#ff9800',
                              color: '#000000',
                              fontFamily: 'monospace',
                              fontWeight: 600,
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {citation.area_measurements && citation.area_measurements.length > 0 && (
                    <Box>
                      <Typography
                        variant="caption"
                        sx={{
                          color: '#2196f3',
                          fontWeight: 600,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                          mb: 0.5,
                        }}
                      >
                        <RulerIcon fontSize="small" />
                        Area Measurements:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {citation.area_measurements.map((measurement, measureIndex) => (
                          <Chip
                            key={measureIndex}
                            label={measurement}
                            size="small"
                            sx={{
                              bgcolor: '#2196f3',
                              color: '#ffffff',
                              fontFamily: 'monospace',
                              fontWeight: 600,
                            }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Box>
              )}

              {/* Chunk ID for reference */}
              <Typography
                variant="caption"
                sx={{
                  color: '#8e8ea0',
                  fontFamily: 'monospace',
                  mt: 1,
                  pl: 5,
                }}
              >
                Ref: {citation.chunk_id}
              </Typography>
            </ListItem>

            {index < citations.length - 1 && (
              <Divider sx={{ bgcolor: '#4d4d4f', mx: 2 }} />
            )}
          </Box>
        ))}
      </List>

      <Typography
        variant="caption"
        sx={{
          color: '#8e8ea0',
          display: 'block',
          textAlign: 'center',
          mt: 2,
          fontStyle: 'italic',
        }}
      >
        All citations are from official Austrian legal documents
      </Typography>
    </Box>
  );
};

export default CitationsList;
