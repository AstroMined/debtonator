import React, { useState } from 'react';
import { Box, ThemeProvider, CssBaseline } from '@mui/material';
import { Navigation } from './Navigation';
import { Sidebar } from './Sidebar';
import { PageContainer } from './PageContainer';
import { theme } from '../../theme';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <Navigation onMenuClick={handleDrawerToggle} />
        <Sidebar
          open={mobileOpen}
          onClose={handleDrawerToggle}
        />
        <PageContainer>
          {children}
        </PageContainer>
      </Box>
    </ThemeProvider>
  );
};
