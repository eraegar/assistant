import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  styled,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import {
  CheckCircle,
  Star,
  Business,
  Person,
  AllInclusive,
  AccessTime,
} from '@mui/icons-material';
import { StatsCard, EnhancedPaper, GradientChip, clientGradients } from './styles';

const PlanCard = styled(StatsCard)(({ theme }) => ({
  position: 'relative',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  '&.recommended': {
    transform: 'scale(1.05)',
    border: '2px solid',
    borderColor: theme.palette.primary.main,
    '&::before': {
      content: '"Рекомендуем"',
      position: 'absolute',
      top: -12,
      left: '50%',
      transform: 'translateX(-50%)',
      background: clientGradients.primary,
      color: 'white',
      padding: '4px 16px',
      borderRadius: 12,
      fontSize: '0.75rem',
      fontWeight: 600,
      zIndex: 1,
    },
  },
}));

interface Plan {
  id: string;
  name: string;
  price: number;
  hoursPerDay: number;
  description: string;
  features: string[];
  recommended?: boolean;
  taskTypes: string[];
}

interface HourOption {
  hours: number;
  price: number;
  description: string;
}

const plans: Plan[] = [
  {
    id: 'personal',
    name: 'Личный ассистент',
    price: 15000,
    hoursPerDay: 5,
    description: 'Для личных задач и домашних дел',
    taskTypes: ['Личные'],
    features: [
      'Личные задачи любой сложности',
      'Помощь в организации быта',
      'Поиск услуг и товаров',
      'Планирование мероприятий',
      'Бронирование и заказы',
      'Поддержка 24/7',
    ],
  },
  {
    id: 'business',
    name: 'Бизнес ассистент',
    price: 50000,
    hoursPerDay: 8,
    description: 'Для профессиональных и рабочих задач',
    taskTypes: ['Бизнес'],
    recommended: true,
    features: [
      'Исследования рынка',
      'Подготовка документов',
      'Организация встреч',
      'Поиск партнеров и клиентов',
      'Административные задачи',
      'Приоритетная поддержка',
    ],
  },
  {
    id: 'full',
    name: 'Личный + Бизнес',
    price: 80000,
    hoursPerDay: 10,
    description: 'Универсальный пакет для всех типов задач',
    taskTypes: ['Личные', 'Бизнес'],
    features: [
      'Все виды личных задач',
      'Все виды бизнес-задач',
      'Максимальная гибкость',
      'Персональный менеджер',
      'VIP поддержка 24/7',
      'Расширенная аналитика',
    ],
  },
];

// Варианты часов для каждого типа плана
const hourOptions: Record<string, HourOption[]> = {
  personal: [
    { hours: 2, price: 15000, description: '2 часа в день' },
    { hours: 5, price: 30000, description: '5 часов в день' },
    { hours: 8, price: 50000, description: '8 часов в день' },
  ],
  business: [
    { hours: 2, price: 30000, description: '2 часа в день' },
    { hours: 5, price: 60000, description: '5 часов в день' },
    { hours: 8, price: 80000, description: '8 часов в день' },
  ],
  full: [
    { hours: 2, price: 40000, description: '2 часа в день' },
    { hours: 5, price: 80000, description: '5 часов в день' },
    { hours: 8, price: 100000, description: '8 часов в день' },
  ],
};

const PlansScreen: React.FC = () => {
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [selectedHours, setSelectedHours] = useState<number>(5);
  const [hourSelectionOpen, setHourSelectionOpen] = useState(false);
  const [currentPlanForHours, setCurrentPlanForHours] = useState<Plan | null>(null);

  const handleSelectPlan = (plan: Plan) => {
    setCurrentPlanForHours(plan);
    setHourSelectionOpen(true);
  };

  const handleHourSelection = (hours: number) => {
    setSelectedHours(hours);
  };

  const handleConfirmHourSelection = () => {
    if (currentPlanForHours) {
      // Обновляем план с выбранными часами
      const updatedPlan = {
        ...currentPlanForHours,
        hoursPerDay: selectedHours,
        price: hourOptions[currentPlanForHours.id].find(option => option.hours === selectedHours)?.price || currentPlanForHours.price
      };
      setSelectedPlan(updatedPlan);
      setHourSelectionOpen(false);
      setCurrentPlanForHours(null);
    }
  };

  const handleCloseHourSelection = () => {
    setHourSelectionOpen(false);
    setCurrentPlanForHours(null);
  };

  const getPlanIcon = (taskTypes: string[]) => {
    if (taskTypes.includes('Личные') && taskTypes.includes('Бизнес')) {
      return <AllInclusive sx={{ fontSize: 40, color: 'primary.main' }} />;
    } else if (taskTypes.includes('Бизнес')) {
      return <Business sx={{ fontSize: 40, color: 'primary.main' }} />;
    } else {
      return <Person sx={{ fontSize: 40, color: 'primary.main' }} />;
    }
  };

  const getTaskTypeChips = (taskTypes: string[]) => {
    return taskTypes.map((type, index) => (
      <GradientChip
        key={index}
        label={type}
        size="small"
        color={type === 'Бизнес' ? 'primary' : 'secondary'}
        sx={{ mr: 1 }}
      />
    ));
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 5 }}>
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            Выберите подходящий план 🚀
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Начните с любого тарифа и обновляйтесь по мере необходимости
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Все планы включают 24/7 поддержку и гарантию качества
          </Typography>
        </Box>

        {/* Plans Grid */}
        <Grid container spacing={4} sx={{ mb: 4 }}>
          {plans.map((plan) => (
            <Grid item xs={12} sm={6} md={4} key={plan.id}>
              <PlanCard
                className={plan.recommended ? 'recommended' : ''}
                onClick={() => handleSelectPlan(plan)}
                sx={{
                  cursor: 'pointer',
                  border: selectedPlan?.id === plan.id ? '2px solid' : '1px solid',
                  borderColor: selectedPlan?.id === plan.id ? 'primary.main' : 'rgba(102, 126, 234, 0.1)',
                }}
              >
                <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  {/* Plan Header */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    {getPlanIcon(plan.taskTypes)}
                    <Typography variant="h6" fontWeight="bold" sx={{ mt: 1, mb: 1 }}>
                      {plan.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {plan.description}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      {getTaskTypeChips(plan.taskTypes)}
                    </Box>
                  </Box>

                  {/* Price */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography variant="h4" fontWeight="bold" color="primary.main">
                      от {plan.price.toLocaleString('ru-RU')} ₽
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      в месяц • от {plan.hoursPerDay}ч/день
                    </Typography>
                  </Box>

                  {/* Features */}
                  <List dense sx={{ flexGrow: 1, mb: 2 }}>
                    {plan.features.map((feature, index) => (
                      <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={feature}
                          primaryTypographyProps={{
                            variant: 'body2',
                            fontSize: '0.85rem'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  {/* Select Button */}
                  <Button
                    variant={selectedPlan?.id === plan.id ? "contained" : "outlined"}
                    fullWidth
                    size="large"
                    onClick={() => handleSelectPlan(plan)}
                    sx={{
                      mt: 'auto',
                      py: 1.5,
                      ...(selectedPlan?.id === plan.id && {
                        background: clientGradients.primary,
                        '&:hover': {
                          background: clientGradients.primary,
                        }
                      }),
                      ...(plan.recommended && selectedPlan?.id !== plan.id && {
                        borderColor: 'primary.main',
                        color: 'primary.main',
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                          transform: 'translateY(-1px)',
                        }
                      })
                    }}
                  >
                    {selectedPlan?.id === plan.id ? (
                      <>
                        <CheckCircle sx={{ mr: 1, fontSize: 20 }} />
                        Выбрано
                      </>
                    ) : (
                      'Выбрать план'
                    )}
                  </Button>

                  {plan.recommended && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                      <GradientChip
                        icon={<Star />}
                        label="Популярный выбор"
                        size="small"
                        color="warning"
                      />
                    </Box>
                  )}
                </CardContent>
              </PlanCard>
            </Grid>
          ))}
        </Grid>

        {/* Selected Plan Summary */}
        {selectedPlan && (
          <EnhancedPaper sx={{ p: 4, mb: 3 }}>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Выбранный план: {selectedPlan.name}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedPlan.description}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {getTaskTypeChips(selectedPlan.taskTypes)}
                </Box>
                <Typography variant="h5" fontWeight="bold" color="primary.main">
                  {selectedPlan.price.toLocaleString('ru-RU')} ₽/месяц
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedPlan.hoursPerDay} часов работы в день
                </Typography>
              </Grid>
              <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'center', md: 'right' } }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Для регистрации и оплаты перейдите в основное приложение
                </Typography>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => window.open('https://t.me/your_bot_username', '_blank')}
                  sx={{
                    py: 2,
                    px: 4,
                    borderColor: 'primary.main',
                    color: 'primary.main',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: 'primary.50',
                    }
                  }}
                >
                  Открыть в Telegram
                </Button>
              </Grid>
            </Grid>
          </EnhancedPaper>
        )}

        {/* Features Comparison */}
        <EnhancedPaper sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ textAlign: 'center', mb: 3 }}>
            Почему выбирают нас? 🌟
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: 2,
                  background: clientGradients.success,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  fontSize: '2rem',
                }}
              >
                ⚡
              </Box>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Быстрое выполнение
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Все задачи выполняются в течение 24 часов с момента постановки
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: 2,
                  background: clientGradients.info,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  fontSize: '2rem',
                }}
              >
                🛡️
              </Box>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Гарантия качества
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Все ассистенты проходят тщательную проверку и имеют высокий рейтинг
              </Typography>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign: 'center' }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: 2,
                  background: clientGradients.warning,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  fontSize: '2rem',
                }}
              >
                💬
              </Box>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                24/7 поддержка
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Круглосуточная поддержка и прямое общение с ассистентами
              </Typography>
            </Grid>
          </Grid>
        </EnhancedPaper>
      </Container>

      {/* Hour Selection Dialog */}
      <Dialog 
        open={hourSelectionOpen} 
        onClose={handleCloseHourSelection}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <AccessTime sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
            <Typography variant="h5" fontWeight="bold">
              Выберите количество часов
            </Typography>
          </Box>
          {currentPlanForHours && (
            <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center' }}>
              {currentPlanForHours.name}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {currentPlanForHours && (
            <Box sx={{ mt: 2 }}>
              <RadioGroup
                value={selectedHours}
                onChange={(e) => handleHourSelection(Number(e.target.value))}
              >
                {hourOptions[currentPlanForHours.id].map((option) => (
                  <Box
                    key={option.hours}
                    sx={{
                      border: selectedHours === option.hours ? '2px solid' : '1px solid',
                      borderColor: selectedHours === option.hours ? 'primary.main' : 'divider',
                      borderRadius: 2,
                      p: 2,
                      mb: 2,
                      backgroundColor: selectedHours === option.hours ? 'primary.50' : 'background.paper',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'primary.50',
                      }
                    }}
                  >
                    <FormControlLabel
                      value={option.hours}
                      control={<Radio />}
                      label={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                          <Box>
                            <Typography variant="h6" fontWeight="bold">
                              {option.hours} часов в день
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {option.description}
                            </Typography>
                          </Box>
                          <Box sx={{ textAlign: 'right' }}>
                            <Typography variant="h5" fontWeight="bold" color="primary.main">
                              {option.price.toLocaleString('ru-RU')} ₽
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              в месяц
                            </Typography>
                          </Box>
                        </Box>
                      }
                      sx={{ width: '100%', m: 0 }}
                    />
                  </Box>
                ))}
              </RadioGroup>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button 
            onClick={handleCloseHourSelection}
            variant="outlined"
            size="large"
          >
            Отмена
          </Button>
          <Button
            onClick={handleConfirmHourSelection}
            variant="contained"
            size="large"
            sx={{
              background: clientGradients.primary,
              '&:hover': {
                background: clientGradients.primary,
              }
            }}
          >
            Подтвердить выбор
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PlansScreen; 