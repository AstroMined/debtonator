import React from 'react';
import { PageContainer } from '../../components/layout';
import { CashflowDisplayContainer } from '../../components/cashflow';

export const CashflowPage: React.FC = () => {
  return (
    <PageContainer title="Cashflow Overview">
      <CashflowDisplayContainer />
    </PageContainer>
  );
};

export default CashflowPage;
