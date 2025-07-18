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
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  styled,
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
  price: number;
  hoursPerDay: number;
  description: string;
  features: string[];
  recommended?: boolean;
  taskTypes: string[];
}

interface TariffCategory {
  id: string;
  name: string;
  description: string;
  taskTypes: string[];
  icon: React.ReactNode;
  hourOptions: {
    hours: number;
    price: number;
    planId: string;
    features: string[];
  }[];
}

const plans: Plan[] = [
  {
    id: 'personal_2h',
    name: 'Личный ассистент',
    price: 15000,
    hoursPerDay: 2,
    description: 'Идеально для личных задач и домашних дел',
    taskTypes: ['Личные'],
    features: [
      'До 2 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Поддержка по email',
      'История задач и отслеживание',
    ],
  },
  {
    id: 'personal_5h',
    name: 'Личный ассистент',
    price: 30000,
    hoursPerDay: 5,
    description: 'Расширенный пакет для активных пользователей',
    taskTypes: ['Личные'],
    features: [
      'До 5 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Приоритетная поддержка',
      'История задач и аналитика',
      'Персональный менеджер',
    ],
  },
  {
    id: 'personal_8h',
    name: 'Личный ассистент',
    price: 50000,
    hoursPerDay: 8,
    description: 'Максимальный пакет для личных задач',
    taskTypes: ['Личные'],
    features: [
      'До 8 часов работы в день',
      'Неограниченные личные задачи',
      'Гарантия выполнения за 24 часа',
      'Прямое общение с ассистентами',
      'Приоритетная поддержка',
      'История задач и аналитика',
      'Персональный менеджер',
      'Расширенная отчетность',
    ],
  },
  {
    id: 'business_2h',
    name: 'Бизнес ассистент',
    price: 30000,
    hoursPerDay: 2,
    description: 'Профессиональная поддержка для бизнеса',
    taskTypes: ['Бизнес'],
    features: [
      'До 2 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'Приоритетная поддержка',
    ],
  },
  {
    id: 'business_5h',
    name: 'Бизнес ассистент',
    price: 60000,
    hoursPerDay: 5,
    description: 'Расширенная поддержка для бизнеса',
    taskTypes: ['Бизнес'],
    recommended: true,
    features: [
      'До 5 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'Приоритетная поддержка 24/7',
      'Интеграция с корпоративными системами',
    ],
  },
  {
    id: 'business_8h',
    name: 'Бизнес ассистент',
    price: 80000,
    hoursPerDay: 8,
    description: 'Максимальная поддержка для бизнеса',
    taskTypes: ['Бизнес'],
    features: [
      'До 8 часов работы в день',
      'Неограниченные бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Бизнес-специализированные ассистенты',
      'Расширенная отчетность',
      'VIP поддержка 24/7',
      'Интеграция с корпоративными системами',
      'Персональный аккаунт-менеджер',
    ],
  },
  {
    id: 'full_2h',
    name: 'Личный + Бизнес',
    price: 40000,
    hoursPerDay: 2,
    description: 'Универсальный пакет для всех типов задач',
    taskTypes: ['Личные', 'Бизнес'],
    features: [
      'До 2 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'Приоритетная поддержка',
    ],
  },
  {
    id: 'full_5h',
    name: 'Личный + Бизнес',
    price: 80000,
    hoursPerDay: 5,
    description: 'Расширенный универсальный пакет',
    taskTypes: ['Личные', 'Бизнес'],
    features: [
      'До 5 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'VIP поддержка 24/7',
      'Доступ к API',
    ],
  },
  {
    id: 'full_8h',
    name: 'Личный + Бизнес',
    price: 100000,
    hoursPerDay: 8,
    description: 'Максимальный пакет для всех типов задач',
    taskTypes: ['Личные', 'Бизнес'],
    features: [
      'До 8 часов работы в день',
      'Неограниченные личные и бизнес-задачи',
      'Гарантия выполнения за 24 часа',
      'Приоритетный подбор ассистентов',
      'Все специализации ассистентов',
      'Расширенная аналитика',
      'VIP поддержка 24/7',
      'Доступ к API',
      'Персональный аккаунт-менеджер',
    ],
  },
];

const tariffCategories: TariffCategory[] = [
  {
    id: 'personal',
    name: 'Личный ассистент',
    description: 'Идеально для личных задач и домашних дел',
    taskTypes: ['Личные'],
    icon: <Person sx={{ fontSize: 40, color: 'primary.main' }} />,
    hourOptions: [
      {
        hours: 2,
        price: 15000,
        planId: 'personal_2h',
        features: [
          'До 2 часов работы в день',
          'Неограниченные личные задачи',
          'Гарантия выполнения за 24 часа',
          'Прямое общение с ассистентами',
          'Поддержка по email',
          'История задач и отслеживание',
        ]
      },
      {
        hours: 5,
        price: 30000,
        planId: 'personal_5h',
        features: [
          'До 5 часов работы в день',
          'Неограниченные личные задачи',
          'Гарантия выполнения за 24 часа',
          'Прямое общение с ассистентами',
          'Приоритетная поддержка',
          'История задач и аналитика',
          'Персональный менеджер',
        ]
      },
      {
        hours: 8,
        price: 50000,
        planId: 'personal_8h',
        features: [
          'До 8 часов работы в день',
          'Неограниченные личные задачи',
          'Гарантия выполнения за 24 часа',
          'Прямое общение с ассистентами',
          'Приоритетная поддержка',
          'История задач и аналитика',
          'Персональный менеджер',
          'Расширенная отчетность',
        ]
      }
    ]
  },
  {
    id: 'business',
    name: 'Бизнес ассистент',
    description: 'Профессиональная поддержка для бизнеса',
    taskTypes: ['Бизнес'],
    icon: <Business sx={{ fontSize: 40, color: 'primary.main' }} />,
    hourOptions: [
      {
        hours: 2,
        price: 30000,
        planId: 'business_2h',
        features: [
          'До 2 часов работы в день',
          'Неограниченные бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Бизнес-специализированные ассистенты',
          'Расширенная отчетность',
          'Приоритетная поддержка',
        ]
      },
      {
        hours: 5,
        price: 60000,
        planId: 'business_5h',
        features: [
          'До 5 часов работы в день',
          'Неограниченные бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Бизнес-специализированные ассистенты',
          'Расширенная отчетность',
          'Приоритетная поддержка 24/7',
          'Интеграция с корпоративными системами',
        ]
      },
      {
        hours: 8,
        price: 80000,
        planId: 'business_8h',
        features: [
          'До 8 часов работы в день',
          'Неограниченные бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Бизнес-специализированные ассистенты',
          'Расширенная отчетность',
          'VIP поддержка 24/7',
          'Интеграция с корпоративными системами',
          'Персональный аккаунт-менеджер',
        ]
      }
    ]
  },
  {
    id: 'full',
    name: 'Полный пакет',
    description: 'Универсальный пакет для всех типов задач',
    taskTypes: ['Личные', 'Бизнес'],
    icon: <AllInclusive sx={{ fontSize: 40, color: 'primary.main' }} />,
    hourOptions: [
      {
        hours: 2,
        price: 40000,
        planId: 'full_2h',
        features: [
          'До 2 часов работы в день',
          'Неограниченные личные и бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Все специализации ассистентов',
          'Расширенная аналитика',
          'Приоритетная поддержка',
        ]
      },
      {
        hours: 5,
        price: 80000,
        planId: 'full_5h',
        features: [
          'До 5 часов работы в день',
          'Неограниченные личные и бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Все специализации ассистентов',
          'Расширенная аналитика',
          'VIP поддержка 24/7',
          'Доступ к API',
        ]
      },
      {
        hours: 8,
        price: 100000,
        planId: 'full_8h',
        features: [
          'До 8 часов работы в день',
          'Неограниченные личные и бизнес-задачи',
          'Гарантия выполнения за 24 часа',
          'Приоритетный подбор ассистентов',
          'Все специализации ассистентов',
          'Расширенная аналитика',
          'VIP поддержка 24/7',
          'Доступ к API',
          'Персональный аккаунт-менеджер',
        ]
      }
    ]
  }
];

const PlansScreen: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<TariffCategory | null>(null);
  const [selectedHourOption, setSelectedHourOption] = useState<{hours: number; price: number; planId: string; features: string[]} | null>(null);
  const [showHourSelection, setShowHourSelection] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleSelectCategory = (category: TariffCategory) => {
    setSelectedCategory(category);
    setShowHourSelection(true);
  };

  const handleSelectHour = (hourOption: {hours: number; price: number; planId: string; features: string[]}) => {
    setSelectedHourOption(hourOption);
  };

  const handleProceedToPayment = () => {
    if (selectedHourOption) {
      window.location.href = `/payment?plan=${selectedHourOption.planId}`;
    }
  };

  const handleBackToCategories = () => {
    setShowHourSelection(false);
    setSelectedCategory(null);
    setSelectedHourOption(null);
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

        {!showHourSelection ? (
          <>
            {/* Category Selection */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography variant="h5" fontWeight="bold" gutterBottom>
                Шаг 1: Выберите тип ассистента 🎯
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Определите, какие задачи вы планируете делегировать
              </Typography>
            </Box>

            <Grid container spacing={4} sx={{ mb: 4 }}>
              {tariffCategories.map((category) => (
                <Grid item xs={12} md={4} key={category.id}>
              <PlanCard 
                    onClick={() => handleSelectCategory(category)}
                sx={{ 
                  cursor: 'pointer',
                      border: '1px solid rgba(102, 126, 234, 0.1)',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 12px 40px rgba(102, 126, 234, 0.15)',
                        borderColor: 'primary.main',
                      }
                }}
              >
                    <CardContent sx={{ p: 4, textAlign: 'center' }}>
                      {category.icon}
                      <Typography variant="h5" fontWeight="bold" sx={{ mt: 2, mb: 2 }}>
                        {category.name}
                      </Typography>
                      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                        {category.description}
                      </Typography>
                      <Box sx={{ mb: 3 }}>
                        {getTaskTypeChips(category.taskTypes)}
                      </Box>
                      <Button
                        variant="outlined"
                        size="large"
                        fullWidth
                        endIcon={<ArrowForward />}
                        sx={{
                          py: 1.5,
                          borderColor: 'primary.main',
                          color: 'primary.main',
                          '&:hover': {
                            borderColor: 'primary.main',
                            background: 'primary.50',
                          }
                        }}
                      >
                        Выбрать
                      </Button>
                    </CardContent>
                  </PlanCard>
                </Grid>
              ))}
            </Grid>
          </>
        ) : (
          <>
            {/* Hour Selection */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
              <Button
                onClick={handleBackToCategories}
                startIcon={<ArrowForward sx={{ transform: 'rotate(180deg)' }} />}
                sx={{ mr: 2 }}
              >
                Назад
              </Button>
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  Шаг 2: Выберите количество часов 🕐
                    </Typography>
                <Typography variant="body1" color="text.secondary">
                  {selectedCategory?.name} • {selectedCategory?.description}
                    </Typography>
                    </Box>
            </Box>

            <Grid container spacing={3} sx={{ mb: 4 }}>
              {selectedCategory?.hourOptions.map((hourOption) => (
                <Grid item xs={12} md={4} key={hourOption.hours}>
                  <PlanCard 
                    onClick={() => handleSelectHour(hourOption)}
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedHourOption?.hours === hourOption.hours ? '2px solid' : '1px solid',
                      borderColor: selectedHourOption?.hours === hourOption.hours ? 'primary.main' : 'rgba(102, 126, 234, 0.1)',
                    }}
                  >
                    <CardContent sx={{ p: 3, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      {/* Hour Header */}
                      <Box sx={{ textAlign: 'center', mb: 3 }}>
                        <Typography variant="h3" fontWeight="bold" color="primary.main">
                          {hourOption.hours}ч
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          в день
                        </Typography>
                  </Box>

                  {/* Price */}
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <Typography variant="h4" fontWeight="bold" color="primary.main">
                          {hourOption.price.toLocaleString('ru-RU')} ₽
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                          в месяц
                    </Typography>
                  </Box>

                  {/* Features */}
                  <List dense sx={{ flexGrow: 1, mb: 2 }}>
                        {hourOption.features.map((feature, index) => (
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
                        variant={selectedHourOption?.hours === hourOption.hours ? "contained" : "outlined"}
                    fullWidth
                    size="large"
                        onClick={() => handleSelectHour(hourOption)}
                    sx={{
                      mt: 'auto',
                      py: 1.5,
                          ...(selectedHourOption?.hours === hourOption.hours && {
                        background: clientGradients.primary,
                        '&:hover': {
                          background: clientGradients.primary,
                        }
                      })
                    }}
                  >
                        {selectedHourOption?.hours === hourOption.hours ? (
                      <>
                        <CheckCircle sx={{ mr: 1, fontSize: 20 }} />
                        Выбрано
                      </>
                    ) : (
                      'Выбрать план'
                    )}
                  </Button>
                </CardContent>
              </PlanCard>
            </Grid>
          ))}
        </Grid>
          </>
        )}

        {/* Selected Plan Summary */}
        {selectedHourOption && selectedCategory && (
          <EnhancedPaper sx={{ p: 4, mb: 3 }}>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  Выбранный план: {selectedCategory.name}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                  {selectedCategory.description}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {getTaskTypeChips(selectedCategory.taskTypes)}
                </Box>
                <Typography variant="h5" fontWeight="bold" color="primary.main">
                  {selectedHourOption.price.toLocaleString('ru-RU')} ₽/месяц
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  До {selectedHourOption.hours} часов работы в день
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
    </Box>
  );
};

export default PlansScreen; 