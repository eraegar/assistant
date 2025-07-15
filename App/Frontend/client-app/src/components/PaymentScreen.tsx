import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useAuthStore } from '../stores/useAuthStore';

const PaymentScreen: React.FC = () => {
  console.log('🚀 PaymentScreen component mounted');
  
  const navigate = () => window.location.href = '/';
  const { user, activateSubscription } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<string>('personal_2h');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔍 PaymentScreen useEffect - checking URL params');
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const planFromUrl = urlParams.get('plan');
      console.log('📋 Plan from URL:', planFromUrl);
      
      if (planFromUrl) {
        console.log('✅ Setting selected plan from URL:', planFromUrl);
        setSelectedPlan(planFromUrl);
      } else {
        console.log('⚠️ No plan in URL, using default');
      }
    } catch (err) {
      console.error('❌ Error parsing URL parameters:', err);
      setError('Ошибка загрузки параметров');
    }
  }, []);

  console.log('🎯 PaymentScreen render - current state:', {
    selectedPlan,
    user: user?.name,
    error
  });

  // Проверка аутентификации
  if (!user) {
    console.log('❌ No user found, showing auth required message');
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Box textAlign="center">
          <Typography variant="h4" gutterBottom>
            Требуется авторизация
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Пожалуйста, войдите в систему для доступа к странице оплаты.
          </Typography>
          <Button variant="contained" onClick={() => window.location.href = '/'}>
            Перейти к входу
          </Button>
        </Box>
      </Container>
    );
  }

  const handleProcessPayment = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      console.log('🔄 Processing payment for plan:', selectedPlan);
      
      // Имитация обработки платежа
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Генерируем токен платежа для примера
      const paymentToken = `payment_${Date.now()}`;
      console.log('💳 Payment token generated:', paymentToken);

      // Активируем подписку
      const success = await activateSubscription(selectedPlan, paymentToken);
      
      if (success) {
        console.log('✅ Payment successful, redirecting to dashboard');
        window.location.href = '/';
      } else {
        setError('Ошибка активации подписки. Пожалуйста, попробуйте еще раз.');
      }
    } catch (e) {
      console.error('❌ Payment error:', e);
      setError('Произошла ошибка при обработке платежа. Попробуйте еще раз.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Заголовок */}
      <Box mb={4}>
        <Button
          startIcon={<ArrowBack />}
          onClick={navigate}
          sx={{ mb: 2 }}
        >
          Назад к планам
        </Button>
        
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Оплата подписки
        </Typography>
      </Box>

      {/* Отображение ошибки */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Информация о плане */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Выбранный план: {selectedPlan}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Пользователь: {user.name}
        </Typography>
      </Box>

      {/* Кнопка оплаты */}
      <Box>
        <Button
          variant="contained"
          size="large"
          fullWidth
          disabled={isProcessing}
          onClick={handleProcessPayment}
          startIcon={isProcessing ? <CircularProgress size={20} /> : null}
          sx={{ py: 2 }}
        >
          {isProcessing 
            ? 'Обработка платежа...' 
            : `Оплатить план ${selectedPlan}`
          }
        </Button>
      </Box>
    </Container>
  );
};

export default PaymentScreen; 