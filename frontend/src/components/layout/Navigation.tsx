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
  Breadcrumbs,
} from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
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

        {!isMobile && (
          <Box sx={{ ml: 4, display: 'flex', flexDirection: 'column' }}>
            <Breadcrumbs
              aria-label="breadcrumb"
              sx={{
                '& .MuiBreadcrumbs-ol': {
                  color: 'white',
                },
                '& .MuiBreadcrumbs-separator': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
              }}
            >
              <Typography
                component={RouterLink}
                to="/"
                sx={{
                  color: 'white',
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                Home
              </Typography>
              <BreadcrumbSection />
            </Breadcrumbs>
          </Box>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, ml: 'auto' }}>
          {!isMobile && (
            <>
              <NavButton to="/accounts" label="Accounts" />
              <NavButton to="/bills" label="Bills" />
              <NavButton to="/income" label="Income" />
              <NavButton to="/cashflow" label="Cashflow" />
            </>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

interface NavButtonProps {
  to: string;
  label: string;
}

const NavButton: React.FC<NavButtonProps> = ({ to, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Button
      component={RouterLink}
      to={to}
      color="inherit"
      sx={{
        textTransform: 'none',
        position: 'relative',
        '&::after': {
          content: '""',
          position: 'absolute',
          bottom: -2,
          left: 0,
          width: '100%',
          height: 2,
          backgroundColor: 'white',
          opacity: isActive ? 1 : 0,
          transition: 'opacity 0.2s',
        },
        '&:hover::after': {
          opacity: 0.7,
        },
      }}
    >
      {label}
    </Button>
  );
};

const BreadcrumbSection: React.FC = () => {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  if (pathSegments.length === 0) return null;

  const currentPage = pathSegments[pathSegments.length - 1];
  return (
    <Typography
      sx={{
        color: 'rgba(255, 255, 255, 0.9)',
        textTransform: 'capitalize',
      }}
    >
      {currentPage}
    </Typography>
  );
};
