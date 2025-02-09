import React from 'react';
import { Box, Container, useTheme } from '@mui/material';

interface PageContainerProps {
  children: React.ReactNode;
}

const DRAWER_WIDTH = 240;
const TOOLBAR_HEIGHT = 64; // AppBar height

export const PageContainer: React.FC<PageContainerProps> = ({ children }) => {
  const theme = useTheme();

  return (
    <Box
      component="main"
      sx={{
        flexGrow: 1,
        minHeight: '100vh',
        pt: `${TOOLBAR_HEIGHT + 24}px`, // toolbar height + padding
        pb: 3,
        pl: { md: `${DRAWER_WIDTH + 24}px` }, // Add drawer width on medium and up
        width: {
          xs: '100%',
          md: `calc(100% - ${DRAWER_WIDTH}px)`,
        },
        backgroundColor: theme.palette.background.default,
      }}
    >
      <Container
        maxWidth="lg"
        sx={{
          px: { xs: 2, sm: 3 },
        }}
      >
        {children}
      </Container>
    </Box>
  );
};
