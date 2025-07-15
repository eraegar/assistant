import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import WelcomeScreen from './components/WelcomeScreen';
import PlansScreen from './components/PlansScreen';
import DashboardScreen from './components/DashboardScreen';
import PaymentScreen from './components/PaymentScreen';
import { useAuthStore } from './stores/useAuthStore';
import { UserStatus } from './types';
import assistantTheme from './theme'; // Import our comprehensive theme

const queryClient = new QueryClient();

const AuthWrapper: React.FC = () => {
  const { userStatus, refreshUser } = useAuthStore();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      refreshUser();
    }
    // eslint-disable-next-line
  }, []);

  console.log('🎯 AuthWrapper - Current userStatus:', userStatus);

  if (userStatus === UserStatus.UNAUTHENTICATED) {
    console.log('🔐 Rendering WelcomeScreen (UNAUTHENTICATED)');
    return <WelcomeScreen />;
  }
  if (userStatus === UserStatus.NEEDS_SUBSCRIPTION) {
    console.log('📋 Rendering PlansScreen (NEEDS_SUBSCRIPTION)');
    return <PlansScreen />;
  }
  if (userStatus === UserStatus.HAS_ACTIVE_SUBSCRIPTION) {
    console.log('✅ Rendering DashboardScreen (HAS_ACTIVE_SUBSCRIPTION)');
    return <DashboardScreen />;
  }
  // fallback
  console.log('🔄 Rendering WelcomeScreen (fallback)');
  return <WelcomeScreen />;
};

const App: React.FC = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider theme={assistantTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<WelcomeScreen />} />
          <Route path="/" element={<AuthWrapper />} />
          <Route path="/payment" element={<PaymentScreen />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;