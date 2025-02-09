import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 3,
            textAlign: 'center',
            gap: 2,
          }}
        >
          <ErrorOutlineIcon color="error" sx={{ fontSize: 48 }} />
          <Typography variant="h6" color="error">
            Something went wrong
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {this.state.error?.message || 'An unexpected error occurred'}
          </Typography>
          <Button variant="contained" onClick={this.handleRetry}>
            Try Again
          </Button>
        </Box>
      );
    }

    return this.props.children;
  }
}
