import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Checkbox,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Badge,
} from '@mui/material';
import {
  Payment,
  Security,
  CheckCircle,
  CreditCard,
  ArrowBack,
  Lock,
  PhoneAndroid,
  AccountBalance,
  Wallet,
  VerifiedUser,
  Info,
  RadioButtonChecked,
  RadioButtonUnchecked,
} from '@mui/icons-material';
import { useAuthStore } from '../stores/useAuthStore';

interface PaymentMethod {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  provider: string;
  isPopular?: boolean;
}

interface PlanDetails {
  id: string;
  name: string;
  price: number;
  features: string[];
  taskTypes: string[];
}

const paymentMethods: PaymentMethod[] = [
  {
    id: 'yookassa_card',
    name: 'Банковская карта',
    description: 'Visa, MasterCard, МИР',
    icon: <CreditCard />,
    provider: 'ЮKassa',
    isPopular: true,
  },
  {
    id: 'yookassa_sbp',
    name: 'Система Быстрых Платежей',
    description: 'Мгновенный перевод через банк',
    icon: <PhoneAndroid />,
    provider: 'СБП',
    isPopular: true,
  },
  {
    id: 'sberbank',
    name: 'Сбербанк Онлайн',
    description: 'Оплата через приложение банка',
    icon: <AccountBalance />,
    provider: 'Сбербанк',
  },
  {
    id: 'yoomoney',
    name: 'ЮMoney',
    description: 'Электронный кошелек',
    icon: <Wallet />,
    provider: 'ЮMoney',
  },
  {
    id: 'qiwi',
    name: 'QIWI Кошелек',
    description: 'Быстрая оплата через QIWI',
    icon: <PhoneAndroid />,
    provider: 'QIWI',
  },
];

const planDetails: Record<string, PlanDetails> = {
  personal_2h: {
    id: 'personal_2h',
    name: 'Личный ассистент (2ч/день)',
    price: 15000,
    features: [
      'До 2 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Поддержка по email',
      'История задач и отслеживание',
    ],
    taskTypes: ['Личные'],
  },
  personal_5h: {
    id: 'personal_5h',
    name: 'Личный ассистент (5ч/день)',
    price: 30000,
    features: [
      'До 5 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Поддержка по email',
      'История задач и отслеживание',
    ],
    taskTypes: ['Личные'],
  },
  personal_8h: {
    id: 'personal_8h',
    name: 'Личный ассистент (8ч/день)',
    price: 50000,
    features: [
      'До 8 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Поддержка по email',
      'История задач и отслеживание',
    ],
    taskTypes: ['Личные'],
  },
  business_2h: {
    id: 'business_2h',
    name: 'Бизнес ассистент (2ч/день)',
    price: 30000,
    features: [
      'До 2 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'Приоритетная поддержка',
    ],
    taskTypes: ['Бизнес'],
  },
  business_5h: {
    id: 'business_5h',
    name: 'Бизнес ассистент (5ч/день)',
    price: 60000,
    features: [
      'До 5 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'Приоритетная поддержка',
    ],
    taskTypes: ['Бизнес'],
  },
  business_8h: {
    id: 'business_8h',
    name: 'Бизнес ассистент (8ч/день)',
    price: 80000,
    features: [
      'До 8 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'Приоритетная поддержка',
    ],
    taskTypes: ['Бизнес'],
  },
  full_2h: {
    id: 'full_2h',
    name: 'Личный + Бизнес ассистент (2ч/день)',
    price: 40000,
    features: [
      'До 2 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'Доступ к API',
    ],
    taskTypes: ['Личные', 'Бизнес'],
  },
  full_5h: {
    id: 'full_5h',
    name: 'Личный + Бизнес ассистент (5ч/день)',
    price: 80000,
    features: [
      'До 5 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'Доступ к API',
    ],
    taskTypes: ['Личные', 'Бизнес'],
  },
  full_8h: {
    id: 'full_8h',
    name: 'Личный + Бизнес ассистент (8ч/день)',
    price: 100000,
    features: [
      'До 8 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'Доступ к API',
    ],
    taskTypes: ['Личные', 'Бизнес'],
  },
};

const steps = ['Выбор плана', 'Платежные данные', 'Подтверждение'];

const PaymentScreen: React.FC = () => {
  console.log('🚀 PaymentScreen component rendering...');
  
  const navigate = () => window.location.href = '/';
  const { user, activateSubscription } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<string>('personal_2h');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<PaymentMethod | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔍 PaymentScreen useEffect - checking URL parameters...');
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const planFromUrl = urlParams.get('plan');
      console.log('📋 Plan from URL:', planFromUrl);
      
      if (planFromUrl && planDetails[planFromUrl]) {
        console.log('✅ Valid plan found, setting selectedPlan to:', planFromUrl);
        setSelectedPlan(planFromUrl);
      } else {
        console.log('⚠️ Invalid or missing plan in URL, using default');
        setError('Неверный план подписки');
      }
    } catch (err) {
      console.error('❌ Error parsing URL parameters:', err);
      setError('Ошибка загрузки параметров');
    }
  }, []);

  console.log('👤 Current user:', user);
  console.log('📋 Selected plan:', selectedPlan);
  console.log('💳 Selected payment method:', selectedPaymentMethod);

  const currentPlan = planDetails[selectedPlan];
  const priceInRubles = currentPlan.price; // Цена уже в рублях

  const handleProcessPayment = async () => {
    if (!agreedToTerms || !selectedPaymentMethod || !user) return;

    setIsProcessing(true);

    try {
      console.log('🔄 Начинаем обработку платежа...');
      // Имитация обработки платежа
      await new Promise(resolve => setTimeout(resolve, 2000));

      // TODO: Реализовать реальную обработку платежей
      // - Создать сессию платежа с платежным провайдером
      // - Перенаправить на страницу оплаты
      // - Обработать коллбэки платежа

      // Генерируем токен платежа для примера
      const paymentToken = `payment_${Date.now()}`;
      console.log('💳 Токен платежа сгенерирован:', paymentToken);

      // Активируем подписку через AuthStore
      const success = await activateSubscription(selectedPlan, paymentToken);
      
      if (success) {
        console.log('🎉 Показываем диалог успешной оплаты...');
        setShowSuccessDialog(true);
      } else {
        alert('Ошибка активации подписки. Пожалуйста, попробуйте еще раз.');
      }
    } catch (e) {
      console.error('❌ Ошибка обработки платежа:', e);
      alert('Произошла ошибка при обработке платежа. Попробуйте еще раз или выберите другой способ оплаты.');
    } finally {
      setIsProcessing(false);
    }
  };

  const canPay = selectedPaymentMethod && agreedToTerms && !isProcessing;

  return (
    <Box>
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
            <Typography variant="body1">
              {error}
            </Typography>
          </Alert>
        )}

        <Grid container spacing={4}>
          {/* Информация о заказе */}
          <Grid item xs={12} md={8}>
            {/* Сводка заказа */}
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Детали заказа
                </Typography>
                
                <Box display="flex" alignItems="center" mb={2}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      bgcolor: 'primary.main',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mr: 2,
                    }}
                  >
                    <CheckCircle sx={{ color: 'white' }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="bold">
                      {currentPlan.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Подписка на 1 месяц
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography>Стоимость подписки:</Typography>
                  <Typography fontWeight="bold" color="primary.main">
                    {priceInRubles.toLocaleString()} ₽
                  </Typography>
                </Box>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Подписка автоматически продлевается каждый месяц. Отменить можно в любое время.
                  </Typography>
                </Alert>
              </CardContent>
            </Card>

            {/* Способы оплаты */}
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Способ оплаты
                </Typography>
                
                <Grid container spacing={2}>
                  {paymentMethods.map((method) => (
                    <Grid item xs={12} key={method.id}>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 2,
                          cursor: 'pointer',
                          border: selectedPaymentMethod?.id === method.id ? '2px solid' : '1px solid',
                          borderColor: selectedPaymentMethod?.id === method.id ? 'primary.main' : 'divider',
                          bgcolor: selectedPaymentMethod?.id === method.id ? 'primary.50' : 'white',
                        }}
                        onClick={() => setSelectedPaymentMethod(method)}
                      >
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Box display="flex" alignItems="center">
                            <Box
                              sx={{
                                width: 48,
                                height: 48,
                                borderRadius: 1,
                                bgcolor: selectedPaymentMethod?.id === method.id ? 'primary.main' : 'grey.100',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                mr: 2,
                              }}
                            >
                              {React.cloneElement(method.icon as React.ReactElement, {
                                sx: { 
                                  color: selectedPaymentMethod?.id === method.id ? 'white' : 'grey.600' 
                                }
                              })}
                            </Box>
                            <Box>
                              <Box display="flex" alignItems="center" gap={1}>
                                <Typography variant="subtitle1" fontWeight="bold">
                                  {method.name}
                                </Typography>
                                {method.isPopular && (
                                  <Chip 
                                    label="Популярно" 
                                    size="small" 
                                    color="warning" 
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                              </Box>
                              <Typography variant="body2" color="text.secondary">
                                {method.description}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {method.provider}
                              </Typography>
                            </Box>
                          </Box>
                          {selectedPaymentMethod?.id === method.id ? 
                            <RadioButtonChecked color="primary" /> : 
                            <RadioButtonUnchecked color="primary" />
                          }
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Боковая панель */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom fontWeight="bold">
                  Что включено
                </Typography>
                
                <Box display="flex" gap={1} mb={2}>
                  {currentPlan.taskTypes.map((type) => (
                    <Chip key={type} label={type} size="small" variant="outlined" />
                  ))}
                </Box>
                
                <List dense>
                  {currentPlan.features.map((feature, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <CheckCircle sx={{ fontSize: 16, color: 'success.main', mr: 1 }} />
                      <ListItemText 
                        primary={feature} 
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>

            {/* Информация о безопасности */}
            <Alert severity="info" icon={<Security />} sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Безопасность платежей</strong><br />
                Все платежи защищены SSL-шифрованием и обрабатываются через сертифицированные платежные системы.
              </Typography>
              <Box display="flex" gap={1} mt={1}>
                {['SSL', 'PCI DSS', '3DS'].map((badge) => (
                  <Chip 
                    key={badge}
                    label={badge} 
                    size="small" 
                    variant="outlined" 
                    sx={{ height: 24, fontSize: '0.7rem' }}
                  />
                ))}
              </Box>
            </Alert>
          </Grid>
        </Grid>

        {/* Согласие с условиями */}
        <Box mt={4}>
          <FormControlLabel
            control={
              <Checkbox
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                color="primary"
              />
            }
            label={
              <Typography variant="body2">
                Я согласен с{' '}
                <Typography component="span" variant="body2" color="primary" sx={{ textDecoration: 'underline', cursor: 'pointer' }}>
                  условиями использования
                </Typography>
                {' '}и{' '}
                <Typography component="span" variant="body2" color="primary" sx={{ textDecoration: 'underline', cursor: 'pointer' }}>
                  политикой конфиденциальности
                </Typography>
              </Typography>
            }
          />
        </Box>

        {/* Кнопка оплаты */}
        <Box mt={3} pb={2}>
          <Button
            variant="contained"
            size="large"
            fullWidth
            disabled={!canPay}
            onClick={handleProcessPayment}
            startIcon={isProcessing ? <CircularProgress size={20} /> : <Payment />}
            sx={{ 
              py: 2,
              bgcolor: canPay ? 'primary.main' : 'grey.300',
              '&:hover': {
                bgcolor: canPay ? 'primary.dark' : 'grey.300',
              }
            }}
          >
            {isProcessing 
              ? 'Обработка платежа...' 
              : `Оплатить ${priceInRubles.toLocaleString()} ₽`
            }
          </Button>
        </Box>
      </Container>

      {/* Диалог успешной оплаты */}
      <Dialog open={showSuccessDialog} onClose={() => {}} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <CheckCircle sx={{ color: 'success.main', mr: 1, fontSize: 28 }} />
            Оплата успешна!
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Подписка "{currentPlan.name}" активирована.
          </Typography>
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Что дальше?</strong><br />
              • Вам будет назначен персональный ассистент<br />
              • Получите доступ ко всем функциям<br />
              • Начните создавать задачи прямо сейчас
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button 
            variant="contained" 
            onClick={() => {
              console.log('🚀 Кнопка "Начать пользоваться" нажата');
              setShowSuccessDialog(false);
              window.location.href = '/';
            }}
            sx={{ bgcolor: 'primary.main' }}
          >
            Начать пользоваться
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PaymentScreen; 