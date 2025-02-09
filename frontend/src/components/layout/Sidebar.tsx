import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Box,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { AccountSummary } from './AccountSummary';
import {
  Dashboard as DashboardIcon,
  Receipt as BillsIcon,
  AttachMoney as IncomeIcon,
  Timeline as CashflowIcon,
  AccountBalance as AccountsIcon,
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const DRAWER_WIDTH = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Bills', icon: <BillsIcon />, path: '/bills' },
  { text: 'Income', icon: <IncomeIcon />, path: '/income' },
  { text: 'Cashflow', icon: <CashflowIcon />, path: '/cashflow' },
  { text: 'Accounts', icon: <AccountsIcon />, path: '/accounts' },
];

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const navigate = useNavigate();

  const drawerContent = (
    <Box sx={{ 
      width: DRAWER_WIDTH,
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Box sx={{ p: 2 }} /> {/* Spacer for AppBar */}
      <Divider />
      <AccountSummary />
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => {
                navigate(item.path);
                if (isMobile) {
                  onClose();
                }
              }}
              selected={location.pathname === item.path}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <ListItemText 
          primary="Debtonator v1.0"
          primaryTypographyProps={{
            variant: 'caption',
            color: 'text.secondary'
          }}
        />
      </Box>
    </Box>
  );

  return isMobile ? (
    <Drawer
      variant="temporary"
      anchor="left"
      open={open}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      sx={{
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  ) : (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          overflowY: 'auto',
        },
      }}
      open
    >
      {drawerContent}
    </Drawer>
  );
};
