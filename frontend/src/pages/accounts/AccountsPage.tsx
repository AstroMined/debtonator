import React from 'react';
import { Typography } from '@mui/material';
import { PageContainer } from '../../components/layout';
import { AccountsTableContainer } from '../../components/accounts';

export const AccountsPage: React.FC = () => {
  return (
    <PageContainer>
      <Typography variant="h4" component="h1" gutterBottom>
        Accounts
      </Typography>
      <AccountsTableContainer />
    </PageContainer>
  );
};
