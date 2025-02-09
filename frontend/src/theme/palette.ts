import { PaletteOptions } from '@mui/material';

export const palette: PaletteOptions = {
  primary: {
    main: '#1976d2', // Blue for primary actions
    light: '#42a5f5',
    dark: '#1565c0',
  },
  secondary: {
    main: '#9c27b0', // Purple for secondary actions
    light: '#ba68c8',
    dark: '#7b1fa2',
  },
  error: {
    main: '#d32f2f', // Red for errors/negative amounts
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02', // Orange for warnings
    light: '#ff9800',
    dark: '#e65100',
  },
  success: {
    main: '#2e7d32', // Green for success/positive amounts
    light: '#4caf50',
    dark: '#1b5e20',
  },
  info: {
    main: '#0288d1', // Light blue for info
    light: '#03a9f4',
    dark: '#01579b',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  background: {
    default: '#f5f5f5', // Light grey background
    paper: '#ffffff', // White surface
  },
  text: {
    primary: 'rgba(0, 0, 0, 0.87)',
    secondary: 'rgba(0, 0, 0, 0.6)',
    disabled: 'rgba(0, 0, 0, 0.38)',
  },
};
