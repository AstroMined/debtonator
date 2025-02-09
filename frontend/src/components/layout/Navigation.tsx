import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  useTheme,
  useMediaQuery,
  Button,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

interface NavigationProps {
  onMenuClick: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({ onMenuClick }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <AppBar position="fixed" color="primary">
      <Toolbar>
        {isMobile && (
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <AccountBalanceWalletIcon sx={{ mr: 2 }} />
        
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            '&:hover': {
              textDecoration: 'none',
            },
          }}
        >
          Debtonator
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {!isMobile && (
            <>
              <Button
                component={RouterLink}
                to="/bills"
                color="inherit"
                sx={{ textTransform: 'none' }}
              >
                Bills
              </Button>
              {/* Add more navigation buttons here */}
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};
