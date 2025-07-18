import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import PlansScreen from './PlansScreen';
import { theme } from './styles';

const App: React.FC = () => (
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <PlansScreen />
  </ThemeProvider>
);

export default App; 