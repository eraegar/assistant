import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  styled,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Star,
  AccountCircle,
  ExitToApp,
  ArrowForward,
  Business,
  Person,
  AllInclusive,
} from '@mui/icons-material';
import { useAuthStore } from '../stores/useAuthStore';
import { StatsCard, EnhancedPaper, GradientChip, clientGradients } from '../styles/gradients';

// Enhanced styled components
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
  priceRange: string; // Changed from single price to range
  priceFrom: number;
  priceTo: number;
  hoursRange: string; // Shows range of hours
  description: string;
  features: string[];
  recommended?: boolean;
  taskTypes: string[];
  subtitle?: string;
}

interface DetailedPlan {
  id: string;
  name: string;
  price: number;
  hours: number;
  recommended?: boolean;
}

const plans: Plan[] = [
  {
    id: 'personal',
    name: 'Личный ассистент',
    priceRange: '15 000 - 50 000 ₽',
    priceFrom: 15000,
    priceTo: 50000,
    hoursRange: '2-8 часов в день',
    subtitle: 'Для личных задач и домашних дел',
    description: 'Помощь с повседневными задачами, планированием и организацией личного времени',
    taskTypes: ['Личные'],
    features: [
      'Личные задачи и поручения',
      'Планирование мероприятий',
      'Бронирование и покупки',
      'Поиск информации',
      'Организация документов',
      'Поддержка 24/7',
      'Выбор объема: 2, 5 или 8 часов в день',
    ],
  },
  {
    id: 'business',
    name: 'Бизнес ассистент',
    priceRange: '30 000 - 80 000 ₽',
    priceFrom: 30000,
    priceTo: 80000,
    hoursRange: '2-8 часов в день',
    subtitle: 'Профессиональная поддержка бизнеса',
    description: 'Специализированная помощь в решении бизнес-задач и развитии компании',
    taskTypes: ['Бизнес'],
    recommended: true,
    features: [
      'Исследование рынка и конкурентов',
      'Подготовка презентаций',
      'Административные задачи',
      'Поиск партнеров и поставщиков',
      'Ведение социальных сетей',
      'Приоритетная поддержка',
      'Выбор объема: 2, 5 или 8 часов в день',
    ],
  },
  {
    id: 'combo',
    name: 'Личный + Бизнес',
    priceRange: '40 000 - 100 000 ₽',
    priceFrom: 40000,
    priceTo: 100000,
    hoursRange: '2-8 часов в день',
    subtitle: 'Универсальное решение',
    description: 'Полная поддержка как в личных вопросах, так и в бизнесе',
    taskTypes: ['Личные', 'Бизнес'],
    features: [
      'Все типы личных задач',
      'Все типы бизнес-задач',
      'Гибкое распределение времени',
      'Приоритетный подбор ассистентов',
      'VIP поддержка 24/7',
      'Персональный менеджер',
      'Выбор объема: 2, 5 или 8 часов в день',
    ],
  },
];

const PlansScreen: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [selectedPlan, setSelectedPlan] = useState<DetailedPlan | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Plan | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Debug: Track selectedPlan changes
  useEffect(() => {
    console.log('🔄 selectedPlan changed:', selectedPlan);
  }, [selectedPlan]);

  const handleSelectPlan = (plan: Plan) => {
    console.log('📋 Plan selected:', plan);
    setSelectedCategory(plan);
    setShowDetailsModal(true);
  };

  const handlePlanDetailSelect = (detailPlan: DetailedPlan) => {
    console.log('🎯 Plan detail selected:', detailPlan);
    setSelectedPlan(detailPlan);
    setShowDetailsModal(false);
    console.log('📋 Modal closed, selectedPlan should be set');
  };

  const handleProceedToPayment = () => {
    console.log('💳 Proceeding to payment, selectedPlan:', selectedPlan);
    if (selectedPlan) {
      console.log('🚀 Navigating to payment page with plan:', selectedPlan.id);
      navigate(`/payment?plan=${selectedPlan.id}`);
    } else {
      console.log('❌ No plan selected for payment');
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleProfileMenuClose();
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

  const getDetailedPlans = (category: Plan): DetailedPlan[] => {
    const baseId = category.id;
    const detailedPlans: DetailedPlan[] = [];
    
    if (baseId === 'personal') {
      detailedPlans.push(
        { id: 'personal_2h', name: 'Личный 2ч', price: 15000, hours: 2 },
        { id: 'personal_5h', name: 'Личный 5ч', price: 30000, hours: 5 },
        { id: 'personal_8h', name: 'Личный 8ч', price: 50000, hours: 8 }
      );
    } else if (baseId === 'business') {
      detailedPlans.push(
        { id: 'business_2h', name: 'Бизнес 2ч', price: 30000, hours: 2 },
        { id: 'business_5h', name: 'Бизнес 5ч', price: 60000, hours: 5, recommended: true },
        { id: 'business_8h', name: 'Бизнес 8ч', price: 80000, hours: 8 }
      );
    } else if (baseId === 'combo') {
      detailedPlans.push(
        { id: 'full_2h', name: 'Комбо 2ч', price: 40000, hours: 2 },
        { id: 'full_5h', name: 'Комбо 5ч', price: 80000, hours: 5 },
        { id: 'full_8h', name: 'Комбо 8ч', price: 100000, hours: 8 }
      );
    }
    
    return detailedPlans;
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ background: clientGradients.header }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'white', fontWeight: 600 }}>
            💎 Выберите тарифный план
          </Typography>
          
          <IconButton
            color="inherit"
            onClick={handleProfileMenuOpen}
          >
            <Avatar sx={{ width: 32, height: 32 }}>
              {user?.email?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
          >
            <MenuItem onClick={handleProfileMenuClose}>
              <AccountCircle sx={{ mr: 1 }} />
              Профиль
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ExitToApp sx={{ mr: 1 }} />
              Выйти
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

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
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {plans.map((plan) => (
            <Grid item xs={12} sm={6} lg={3} key={plan.id}>
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
                      {plan.priceRange}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {plan.hoursRange}
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
            {console.log('🎯 Rendering selected plan summary for:', selectedPlan)}
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Выбранный план: {selectedPlan.name}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedPlan.hours} часов в день
                </Typography>
                <Typography variant="h5" fontWeight="bold" color="primary.main">
                  {selectedPlan.price.toLocaleString('ru-RU')} ₽/месяц
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {(selectedPlan.price / selectedPlan.hours).toLocaleString('ru-RU')} ₽ за час
                </Typography>
              </Grid>
              <Grid item xs={12} md={4} sx={{ textAlign: { xs: 'center', md: 'right' } }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleProceedToPayment}
                  endIcon={<ArrowForward />}
                  sx={{
                    py: 2,
                    px: 4,
                    background: clientGradients.primary,
                    '&:hover': {
                      background: clientGradients.primary,
                      transform: 'translateY(-1px)',
                      boxShadow: '0 6px 20px rgba(102, 126, 234, 0.3)',
                    }
                  }}
                >
                  Перейти к оплате
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

      {/* Plan Details Modal */}
      <Dialog 
        open={showDetailsModal} 
        onClose={() => setShowDetailsModal(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          }
        }}
      >
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          <Typography variant="h5" fontWeight="bold">
            {selectedCategory?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {selectedCategory?.subtitle}
          </Typography>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          <Typography variant="body1" sx={{ mb: 3, textAlign: 'center' }}>
            {selectedCategory?.description}
          </Typography>
          
          <Grid container spacing={2}>
            {selectedCategory && getDetailedPlans(selectedCategory).map((plan) => (
              <Grid item xs={12} md={4} key={plan.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    border: plan.recommended ? '2px solid' : '1px solid',
                    borderColor: plan.recommended ? 'primary.main' : 'divider',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    }
                  }}
                  onClick={() => handlePlanDetailSelect(plan)}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    {plan.recommended && (
                      <Box sx={{ mb: 1 }}>
                        <Chip 
                          label="Популярный" 
                          color="primary" 
                          size="small"
                          icon={<Star />}
                        />
                      </Box>
                    )}
                    
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {plan.name}
                    </Typography>
                    
                    <Typography variant="h4" fontWeight="bold" color="primary.main" gutterBottom>
                      {plan.price.toLocaleString('ru-RU')} ₽
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {plan.hours} часов в день
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary">
                      {(plan.price / plan.hours).toLocaleString('ru-RU')} ₽ за час
                    </Typography>
                    
                    <Button
                      variant="contained"
                      fullWidth
                      sx={{ mt: 2 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePlanDetailSelect(plan);
                      }}
                    >
                      Выбрать
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button 
            onClick={() => setShowDetailsModal(false)}
            color="inherit"
          >
            Назад
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PlansScreen; 