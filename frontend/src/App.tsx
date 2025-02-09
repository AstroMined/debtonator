import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { AppLayout } from './components/layout';
import { HomePage, BillsPage, IncomePage, CashflowPage } from './pages';

function App() {
  return (
    <BrowserRouter>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <AppLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/bills" element={<BillsPage />} />
            {/* Add more routes as they are implemented */}
            <Route path="/income" element={<IncomePage />} />
            <Route path="/cashflow" element={<CashflowPage />} />
            <Route path="/accounts" element={<div>Accounts page coming soon</div>} />
          </Routes>
        </AppLayout>
      </LocalizationProvider>
    </BrowserRouter>
  );
}

export default App;
