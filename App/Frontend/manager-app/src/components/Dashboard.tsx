import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Box, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  AppBar,
  Toolbar,
  IconButton,
  styled,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  TablePagination,
  Tooltip,
  Fab,
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  People as PeopleIcon,
  Person as PersonIcon,
  AttachMoney as MoneyIcon,
  Logout as LogoutIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Business as BusinessIcon,
  SwapHoriz as ReassignIcon,
  PersonAdd as AssignIcon,
  RemoveCircle as UnassignIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Add as AddIcon,
  SupervisorAccount as SupervisorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useManagerStore } from '../stores/useManagerStore';
import { managerGradients } from '../theme';
import { formatPhoneNumber, getCleanPhoneNumber, isValidPhoneNumber } from '../utils/phoneFormatter';

// API base URL
const API_BASE_URL = 'https://api.rent-assistant.ru';

// Styled components for enhanced design
const StatsCard = styled(Card)(({ theme }) => ({
  background: managerGradients.card,
  borderRadius: 16,
  transition: 'all 0.3s ease-in-out',
  border: '1px solid rgba(25, 118, 210, 0.1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 40px rgba(25, 118, 210, 0.15)',
  },
}));

const EnhancedPaper = styled(Paper)(({ theme }) => ({
  borderRadius: 16,
  background: managerGradients.card,
  border: '1px solid rgba(25, 118, 210, 0.08)',
}));

const GradientChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  fontWeight: 500,
  '&.MuiChip-colorPrimary': {
    background: managerGradients.primary,
  },
  '&.MuiChip-colorSecondary': {
    background: managerGradients.secondary,
  },
  '&.MuiChip-colorWarning': {
    background: managerGradients.warning,
  },
}));

interface OverviewData {
  tasks: {
    total: number;
    pending: number;
    in_progress: number;
    completed: number;
    new_this_week: number;
  };
  assistants: {
    total_active: number;
    online_now: number;
    with_active_tasks: number;
    avg_tasks_per_assistant: number;
  };
  clients: {
    total_active: number;
    active_subscribers: number;
    new_this_week: number;
    subscription_distribution: Record<string, number>;
  };
  performance: {
    task_completion_rate: number;
    assistant_utilization: number;
    monthly_revenue: number;
  };
}

interface Task {
  id: number;
  title: string;
  description: string;
  type: string;
  status: string;
  created_at: string;
  deadline: string | null;
  claimed_at: string | null;
  completed_at: string | null;
  result: string | null;
  completion_notes: string | null;
  client_rating: number | null;
  client_feedback: string | null;
  client: {
    id: number;
    name: string;
    phone: string;
  };
  assistant: {
    id: number;
    name: string;
    specialization: string;
  } | null;
}

interface Assistant {
  id: number;
  name: string;
  email: string;
  phone?: string;
  telegram_username?: string;
  password?: string;
  specialization: string;
  status: string;
  current_active_tasks: number;
  total_tasks_completed: number;
  average_rating: number;
  is_available?: boolean;
  last_active: string | null;
  recent_tasks_week?: number;
  created_at?: string;
  last_known_password?: string;
  last_password_reset_at?: string;
}

interface Client {
  id: number;
  name: string;
  email: string;
  phone: string;
  telegram_username: string | null;
  total_tasks: number;
  active_tasks: number;
  created_at: string;
  assigned_assistants?: Array<{
    id: number;
    name: string;
    specialization: string;
    status: string;
    current_active_tasks: number;
    is_primary: boolean;
    allowed_task_types: string[];
    assignment_id: number;
    assigned_at: string;
  }>;
  subscription: {
    id: number;
    plan: string;
    status: string;
    started_at: string;
    expires_at: string | null;
    auto_renew: boolean;
  } | null;
}

const Dashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskPage, setTaskPage] = useState(0);
  const [taskRowsPerPage, setTaskRowsPerPage] = useState(10);
  const [taskFilter, setTaskFilter] = useState('');
  const [assistantPage, setAssistantPage] = useState(0);
  const [assistantRowsPerPage, setAssistantRowsPerPage] = useState(10);
  const [reassignDialogOpen, setReassignDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [availableAssistants, setAvailableAssistants] = useState<Assistant[]>([]);
  const [selectedAssistant, setSelectedAssistant] = useState<number | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [clientPage, setClientPage] = useState(0);
  const [clientRowsPerPage, setClientRowsPerPage] = useState(10);
  const [clientFilter, setClientFilter] = useState('');
  const [subscriptionFilter, setSubscriptionFilter] = useState('');
  
  // New state for assistant creation
  const [createAssistantDialogOpen, setCreateAssistantDialogOpen] = useState(false);
  const [newAssistant, setNewAssistant] = useState({
    name: '',
    phone: '',
    email: '',
    password: '',
    specialization: 'personal_only',
    telegram_username: ''
  });
  
  // New state for client assignment
  const [assignClientDialogOpen, setAssignClientDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [assignmentAssistant, setAssignmentAssistant] = useState<number | null>(null);
  const [assignmentType, setAssignmentType] = useState<'primary' | 'additional'>('primary');
  
  // New state for assistant profile dialog
  const [assistantProfileDialogOpen, setAssistantProfileDialogOpen] = useState(false);
  const [selectedAssistantProfile, setSelectedAssistantProfile] = useState<Assistant | null>(null);
  
  // New state for password reset
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [newPassword, setNewPassword] = useState<string>('');
  
  // New state for client profile dialog
  const [clientProfileDialogOpen, setClientProfileDialogOpen] = useState(false);
  const [selectedClientProfile, setSelectedClientProfile] = useState<Client | null>(null);
  
  const { manager, logout } = useManagerStore();

  // Function to open assistant profile dialog
  const openAssistantProfileDialog = (assistant: Assistant) => {
    setSelectedAssistantProfile(assistant);
    setAssistantProfileDialogOpen(true);
  };

  useEffect(() => {
    loadOverview();
  }, []);

  useEffect(() => {
    if (currentTab === 1) {
      loadTasks();
    } else if (currentTab === 2) {
      loadAssistants();
    } else if (currentTab === 3) {
      loadClients();
    }
  }, [currentTab]);

  // Перезагружаем клиентов при изменении фильтра подписки
  useEffect(() => {
    if (currentTab === 3) {
      loadClients();
    }
  }, [subscriptionFilter]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('manager_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const loadOverview = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/management/dashboard/overview`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setOverviewData(data);
      } else {
        throw new Error('Ошибка загрузки аналитики');
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/management/tasks`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks);
      } else {
        throw new Error('Ошибка загрузки задач');
      }
    } catch (error) {
      console.error('Ошибка загрузки задач:', error);
      setError('Ошибка загрузки задач');
    } finally {
      setLoading(false);
    }
  };

  const loadAssistants = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/management/assistants`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setAssistants(data.assistants);
      } else {
        throw new Error('Ошибка загрузки ассистентов');
      }
    } catch (error) {
      console.error('Ошибка загрузки ассистентов:', error);
      setError('Ошибка загрузки ассистентов');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableAssistants = async (taskType: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/management/assistants/available?task_type=${taskType}`, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Available assistants loaded:', data);
        setAvailableAssistants(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка загрузки доступных ассистентов');
      }
    } catch (error) {
      console.error('Ошибка загрузки доступных ассистентов:', error);
      setError(error instanceof Error ? error.message : 'Ошибка загрузки доступных ассистентов');
    }
  };

  const handleTaskReassign = async (taskId: number, assistantId: number | null) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/management/tasks/${taskId}/reassign`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ assistant_id: assistantId })
      });
      
      if (response.ok) {
        const result = await response.json();
        setError(null);
        setReassignDialogOpen(false);
        setSelectedTask(null);
        setSelectedAssistant(null);
        loadTasks(); // Refresh tasks
        // Show success message
        setError(result.message);
        setTimeout(() => setError(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка переназначения задачи');
      }
    } catch (error) {
      console.error('Ошибка переназначения:', error);
      setError(error instanceof Error ? error.message : 'Ошибка переназначения задачи');
    }
  };

  const openReassignDialog = async (task: Task) => {
    setSelectedTask(task);
    await loadAvailableAssistants(task.type);
    setReassignDialogOpen(true);
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      'pending': 'Ожидает',
      'in_progress': 'В работе',
      'completed': 'Завершена',
      'approved': 'Одобрена',
      'cancelled': 'Отменена',
      'rejected': 'Отклонена',
      'online': 'В сети',
      'offline': 'Не в сети',
      'active': 'Активна',
      'expired': 'Истекла',
      'personal': 'Личное',
      'business': 'Бизнес',
      'personal_only': 'Только личные',
      'full_access': 'Полный доступ',
      'business_only': 'Только бизнес',
      // Планы подписок
      'personal_2h': 'Личный 2ч',
      'personal_5h': 'Личный 5ч',
      'personal_8h': 'Личный 8ч',
      'business_2h': 'Бизнес 2ч',
      'business_5h': 'Бизнес 5ч',
      'business_8h': 'Бизнес 8ч',
      'full_2h': 'Полный 2ч',
      'full_5h': 'Полный 5ч',
      'full_8h': 'Полный 8ч'
    };
    return statusMap[status] || status;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'in_progress': return 'info';
      case 'completed': return 'success';
      case 'approved': return 'success';
      case 'cancelled': return 'error';
      case 'rejected': return 'secondary';
      case 'online': return 'success';
      case 'offline': return 'default';
      default: return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderOverviewTab = () => {
    if (!overviewData) return <CircularProgress />;

    return (
      <Box>
        {/* Welcome Section */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            Добро пожаловать, {manager?.name}! 📊
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Панель управления и аналитики
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Key Metrics Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TaskIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Всего задач
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData.tasks.total}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      +{overviewData.tasks.new_this_week} за неделю
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PeopleIcon color="secondary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Ассистенты
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData.assistants.online_now}/{overviewData.assistants.total_active}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Онлайн/Всего
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon color="info" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Клиенты
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData.clients.total_active}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      +{overviewData.clients.new_this_week} за неделю
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <MoneyIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Месячный доход
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData.performance.monthly_revenue?.toLocaleString('ru-RU') || '0'} ₽
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {overviewData.clients.active_subscribers} подписчиков
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          {/* Performance Metrics */}
          <Grid item xs={12} md={6}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Производительность задач
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="warning.main">
                      {overviewData.tasks.pending}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ожидают
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="info.main">
                      {overviewData.tasks.in_progress}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      В работе
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="success.main">
                      {overviewData.tasks.completed}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Завершены
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight="bold" color="primary.main">
                      {overviewData.performance.task_completion_rate}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Выполнение
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </EnhancedPaper>
          </Grid>

          <Grid item xs={12} md={6}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Распределение подписок
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                {Object.entries(overviewData.clients.subscription_distribution).map(([plan, count]) => (
                  <Box key={plan} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <GradientChip 
                      label={getStatusText(plan)} 
                      color="primary" 
                      size="small" 
                      variant="outlined"
                    />
                    <Typography variant="h6" fontWeight="bold" color="primary.main">
                      {count}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </EnhancedPaper>
          </Grid>

          {/* Utilization Metrics */}
          <Grid item xs={12}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Показатели эффективности
                </Typography>
                <Button 
                  variant="outlined" 
                  size="small" 
                  sx={{ ml: 'auto' }}
                  onClick={loadOverview}
                  startIcon={<RefreshIcon />}
                >
                  Обновить
                </Button>
              </Box>
              <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="success.main" gutterBottom>
                      {overviewData.performance.monthly_revenue?.toLocaleString('ru-RU') || '0'} ₽
                    </Typography>
                    <Typography variant="subtitle1" fontWeight={500}>
                      Месячный доход
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      От {overviewData.clients.active_subscribers} подписчиков
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight="bold" color="warning.main" gutterBottom>
                      {overviewData.performance.assistant_utilization}%
                    </Typography>
                    <Typography variant="subtitle1" fontWeight={500}>
                      Загрузка ассистентов
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Процент активных ассистентов
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </EnhancedPaper>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderTasksTab = () => {
    if (loading) return <CircularProgress />;

    const filteredTasks = tasks.filter(task => 
      task.title.toLowerCase().includes(taskFilter.toLowerCase()) ||
      task.description.toLowerCase().includes(taskFilter.toLowerCase()) ||
      task.client.name.toLowerCase().includes(taskFilter.toLowerCase())
    );

    const paginatedTasks = filteredTasks.slice(
      taskPage * taskRowsPerPage,
      taskPage * taskRowsPerPage + taskRowsPerPage
    );

    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight="bold">
            Управление задачами
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder="Поиск задач..."
              value={taskFilter}
              onChange={(e) => setTaskFilter(e.target.value)}
              sx={{ minWidth: 200 }}
            />
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadTasks}
            >
              Обновить
            </Button>
          </Box>
        </Box>

        <EnhancedPaper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>Клиент</TableCell>
                  <TableCell>Тип</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Ассистент</TableCell>
                  <TableCell>Создана</TableCell>
                  <TableCell>Дедлайн</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedTasks.map((task) => (
                  <TableRow key={task.id} hover>
                    <TableCell>{task.id}</TableCell>
                    <TableCell>
                      <Tooltip title={task.description}>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                          {task.title}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>{task.client.name}</TableCell>
                    <TableCell>
                      <GradientChip
                        label={getStatusText(task.type)}
                        size="small"
                        color={task.type === 'business' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(task.status)}
                        size="small"
                        color={getStatusColor(task.status) as any}
                      />
                    </TableCell>
                    <TableCell>
                      {task.assistant ? (
                        <Box>
                          <Typography variant="body2">
                            {task.assistant.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {getStatusText(task.assistant.specialization)}
                          </Typography>
                        </Box>
                      ) : (
                        <Chip label="Не назначен" size="small" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(task.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {task.deadline ? (
                        <Typography variant="body2" color={
                          new Date(task.deadline) < new Date() ? 'error.main' : 'text.primary'
                        }>
                          {formatDate(task.deadline)}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Не установлен
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Переназначить">
                          <IconButton
                            size="small"
                            onClick={() => openReassignDialog(task)}
                            color="primary"
                          >
                            <ReassignIcon />
                          </IconButton>
                        </Tooltip>
                        {task.assistant && (
                          <Tooltip title="Снять с задачи">
                            <IconButton
                              size="small"
                              onClick={() => handleTaskReassign(task.id, null)}
                              color="warning"
                            >
                              <UnassignIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={filteredTasks.length}
            page={taskPage}
            onPageChange={(_, newPage) => setTaskPage(newPage)}
            rowsPerPage={taskRowsPerPage}
            onRowsPerPageChange={(e) => setTaskRowsPerPage(parseInt(e.target.value, 10))}
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
            labelRowsPerPage="Строк на странице:"
          />
        </EnhancedPaper>
      </Box>
    );
  };

  const renderAssistantsTab = () => {
    if (loading) return <CircularProgress />;

    const paginatedAssistants = assistants.slice(
      assistantPage * assistantRowsPerPage,
      assistantPage * assistantRowsPerPage + assistantRowsPerPage
    );

    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight="bold">
            Управление ассистентами
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setCreateAssistantDialogOpen(true)}
              color="primary"
            >
              Создать ассистента
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadAssistants}
            >
              Обновить
            </Button>
          </Box>
        </Box>

        <EnhancedPaper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Имя</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Специализация</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Активные задачи</TableCell>
                  <TableCell>Выполнено</TableCell>
                  <TableCell>Рейтинг</TableCell>
                  <TableCell>Последняя активность</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedAssistants.map((assistant) => (
                  <TableRow key={assistant.id} hover>
                    <TableCell>{assistant.id}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {assistant.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{assistant.email}</TableCell>
                    <TableCell>
                      <GradientChip
                        label={getStatusText(assistant.specialization)}
                        size="small"
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(assistant.status)}
                        size="small"
                        color={getStatusColor(assistant.status) as any}
                        icon={assistant.status === 'online' ? <CheckCircleIcon /> : <ErrorIcon />}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color={
                        assistant.current_active_tasks >= 5 ? 'error.main' : 
                        assistant.current_active_tasks >= 3 ? 'warning.main' : 'text.primary'
                      }>
                        {assistant.current_active_tasks}/5
                      </Typography>
                    </TableCell>
                    <TableCell>{assistant.total_tasks_completed}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2">
                          {assistant.average_rating.toFixed(1)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                          ★
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {assistant.last_active ? formatDate(assistant.last_active) : 'Никогда'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Просмотр профиля ассистента">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => openAssistantProfileDialog(assistant)}
                        >
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={assistants.length}
            page={assistantPage}
            onPageChange={(_, newPage) => setAssistantPage(newPage)}
            rowsPerPage={assistantRowsPerPage}
            onRowsPerPageChange={(e) => setAssistantRowsPerPage(parseInt(e.target.value, 10))}
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
            labelRowsPerPage="Строк на странице:"
          />
        </EnhancedPaper>
      </Box>
    );
  };

  const renderClientsTab = () => {
    if (loading) return <CircularProgress />;

    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" fontWeight="bold">
            Управление клиентами
          </Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadClients}
          >
            Обновить
          </Button>
        </Box>

        {/* Client Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Всего клиентов
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData?.clients.total_active || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      +{overviewData?.clients.new_this_week || 0} за неделю
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircleIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Активные подписки
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData?.clients.active_subscribers || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Платящие клиенты
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <MoneyIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Средний чек
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {overviewData?.performance.monthly_revenue && overviewData?.clients.active_subscribers 
                        ? Math.round((overviewData.performance.monthly_revenue / overviewData.clients.active_subscribers) / 1000) + 'К'
                        : '0'} ₽
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      За подписку
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>


        </Grid>

        {/* Subscription Distribution Chart */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Распределение подписок
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                {overviewData?.clients.subscription_distribution && Object.entries(overviewData.clients.subscription_distribution).map(([plan, count]) => {
                  const planNames: Record<string, { name: string; price: string }> = {
                    // Original detailed plans
                    'personal_2h': { name: 'Личный 2ч', price: '15К ₽' },
                    'personal_5h': { name: 'Личный 5ч', price: '30К ₽' },
                    'personal_8h': { name: 'Личный 8ч', price: '50К ₽' },
                    'business_2h': { name: 'Бизнес 2ч', price: '30К ₽' },
                    'business_5h': { name: 'Бизнес 5ч', price: '60К ₽' },
                    'business_8h': { name: 'Бизнес 8ч', price: '80К ₽' },
                    'full_2h': { name: 'Комбо 2ч', price: '40К ₽' },
                    'full_5h': { name: 'Комбо 5ч', price: '80К ₽' },
                    'full_8h': { name: 'Комбо 8ч', price: '100К ₽' },
                    // New simplified categories
                    'personal': { name: 'Личный ассистент', price: '15-50К ₽' },
                    'business': { name: 'Бизнес ассистент', price: '30-80К ₽' },
                    'combo': { name: 'Личный + Бизнес', price: '40-100К ₽' },
                    'full': { name: 'Личный + Бизнес', price: '40-100К ₽' }
                  };
                  const planInfo = planNames[plan] || { name: plan, price: '—' };
                  return (
                    <Box key={plan} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                      <Box>
                        <Typography variant="body2" fontWeight={500}>
                          {planInfo.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {planInfo.price}/мес
                        </Typography>
                      </Box>
                      <GradientChip 
                        label={`${count} чел.`}
                        color="primary" 
                        size="small"
                      />
                    </Box>
                  );
                })}
              </Box>
            </EnhancedPaper>
          </Grid>

          <Grid item xs={12} md={6}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  Клиентская аналитика
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.50', borderRadius: 2 }}>
                    <Typography variant="h5" fontWeight="bold" color="success.main">
                      {overviewData?.performance.monthly_revenue?.toLocaleString('ru-RU') || '0'} ₽
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Месячный доход
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.50', borderRadius: 2 }}>
                    <Typography variant="h5" fontWeight="bold" color="info.main">
                      {overviewData?.clients.active_subscribers || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Активных подписок
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.50', borderRadius: 2 }}>
                    <Typography variant="h5" fontWeight="bold" color="warning.main">
                      {overviewData?.clients.total_active || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Всего клиентов
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'secondary.50', borderRadius: 2 }}>
                    <Typography variant="h5" fontWeight="bold" color="secondary.main">
                      {overviewData?.clients.new_this_week || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Новых за неделю
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </EnhancedPaper>
          </Grid>
        </Grid>

        {/* Clients Table */}
        <EnhancedPaper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Box>
              <Typography variant="h6" fontWeight="bold">
                Список клиентов
              </Typography>
                <Typography variant="body2" color="text.secondary">
                  {subscriptionFilter === '' ? 'Показаны только клиенты с активными подписками' :
                   subscriptionFilter === 'expired' ? 'Показаны клиенты с истекшими подписками' :
                   'Показаны все клиенты (включая без подписки)'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <TextField
                  size="small"
                  placeholder="Поиск клиентов..."
                  value={clientFilter}
                  onChange={(e) => setClientFilter(e.target.value)}
                  sx={{ minWidth: 200 }}
                />
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Фильтр</InputLabel>
                  <Select
                    value={subscriptionFilter}
                    onChange={(e) => setSubscriptionFilter(e.target.value)}
                    label="Фильтр"
                  >
                    <MenuItem value="">Активные подписки</MenuItem>
                    <MenuItem value="expired">Истекшие подписки</MenuItem>
                    <MenuItem value="all">Все клиенты</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Имя</TableCell>
                  <TableCell>Подписка</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Задач</TableCell>
                  <TableCell>Назначенные ассистенты</TableCell>
                  <TableCell>Регистрация</TableCell>
                  <TableCell>Действия</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {clients.map((client) => (
                  <TableRow key={client.id} hover>
                    <TableCell>{client.id}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {client.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {client.subscription ? (
                        <Box>
                          <GradientChip
                            label={getSubscriptionPlanName(client.subscription.plan)}
                            color="primary"
                            size="small"
                          />
                          <Typography variant="caption" display="block" color="text.secondary">
                            до {new Date(client.subscription.expires_at || '').toLocaleDateString('ru-RU')}
                          </Typography>
                        </Box>
                      ) : (
                        <Chip label="Без подписки" size="small" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell>
                      {client.subscription ? (
                        <Chip
                          label={getStatusText(client.subscription.status)}
                          size="small"
                          color={getStatusColor(client.subscription.status) as any}
                        />
                      ) : (
                        <Chip label="Нет подписки" size="small" color="default" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          Всего: {client.total_tasks}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Активных: {client.active_tasks}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {client.assigned_assistants && client.assigned_assistants.length > 0 ? (
                        <Box>
                          {client.assigned_assistants.map((assistant) => (
                            <Box key={assistant.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                              <GradientChip
                                label={assistant.name}
                                size="small"
                                color="secondary"
                              />
                              <Tooltip title={`Специализация: ${getStatusText(assistant.specialization)}`}>
                                <Typography variant="caption" color="text.secondary">
                                  ({assistant.allowed_task_types.join(', ')})
                                </Typography>
                              </Tooltip>
                            </Box>
                          ))}

                        </Box>
                      ) : (
                        <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          Не назначен
                        </Typography>
                        </Box>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(client.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Просмотр профиля клиента">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => openClientProfileDialog(client)}
                          >
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                        {client.assigned_assistants && client.assigned_assistants.length > 0 ? (
                          <Tooltip title="Отменить назначение ассистента">
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={() => handleUnassignClient(client)}
                            >
                              <UnassignIcon />
                            </IconButton>
                          </Tooltip>
                        ) : (
                        <Tooltip title="Назначить ассистента">
                          <IconButton
                            size="small"
                            color="info"
                            onClick={() => openAssignClientDialog(client)}
                          >
                            <AssignIcon />
                          </IconButton>
                        </Tooltip>
                        )}
                        <Tooltip title="Управление подпиской">
                          <IconButton
                            size="small"
                            color="secondary"
                            onClick={() => openSubscriptionDialog(client)}
                          >
                            <BusinessIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={clients.length}
            page={clientPage}
            onPageChange={(_, newPage) => setClientPage(newPage)}
            rowsPerPage={clientRowsPerPage}
            onRowsPerPageChange={(e) => setClientRowsPerPage(parseInt(e.target.value, 10))}
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
            labelRowsPerPage="Строк на странице:"
          />
        </EnhancedPaper>
      </Box>
    );
  };

  const loadClients = async () => {
    try {
      setLoading(true);
      
      // Формируем URL с фильтром подписки
      let url = `${API_BASE_URL}/api/v1/management/clients`;
      if (subscriptionFilter) {
        url += `?subscription_status=${subscriptionFilter}`;
      }
      
      const response = await fetch(url, {
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const data = await response.json();
        setClients(data.clients);
      } else {
        throw new Error('Ошибка загрузки клиентов');
      }
    } catch (error) {
      console.error('Ошибка загрузки клиентов:', error);
      setError('Ошибка загрузки клиентов');
    } finally {
      setLoading(false);
    }
  };

  const getSubscriptionPlanName = (plan: string) => {
    const planNames: Record<string, string> = {
      // Original detailed plans
      'personal_2h': 'Личный 2ч',
      'personal_5h': 'Личный 5ч', 
      'personal_8h': 'Личный 8ч',
      'business_2h': 'Бизнес 2ч',
      'business_5h': 'Бизнес 5ч',
      'business_8h': 'Бизнес 8ч',
      'full_2h': 'Комбо 2ч',
      'full_5h': 'Комбо 5ч',
      'full_8h': 'Комбо 8ч',
      // New simplified categories
      'personal': 'Личный ассистент',
      'business': 'Бизнес ассистент', 
      'combo': 'Личный + Бизнес',
      'full': 'Личный + Бизнес' // Alias for combo
    };
    return planNames[plan] || plan;
  };

  const openClientProfileDialog = (client: Client) => {
    setSelectedClientProfile(client);
    setClientProfileDialogOpen(true);
  };

  const openSubscriptionDialog = (client: Client) => {
    // TODO: Implement subscription management dialog
    console.log('Open subscription dialog:', client);
  };

  // New functions for assistant creation and client assignment
  const handleCreateAssistant = async () => {
    try {
      // Prepare assistant data with clean phone number
      const assistantDataToSend = {
        ...newAssistant,
        phone: getCleanPhoneNumber(newAssistant.phone) // Ensure clean format for API
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/management/assistants/create`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(assistantDataToSend)
      });
      
      if (response.ok) {
        const result = await response.json();
        setError(`Ассистент ${result.name} успешно создан!`);
        setCreateAssistantDialogOpen(false);
        setNewAssistant({
          name: '',
          phone: '',
          email: '',
          password: '',
          specialization: 'personal_only',
          telegram_username: ''
        });
        await loadAssistants(); // Refresh assistants list
        setTimeout(() => setError(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка создания ассистента');
      }
    } catch (error) {
      console.error('Ошибка создания ассистента:', error);
      setError(error instanceof Error ? error.message : 'Ошибка создания ассистента');
    }
  };

  // Phone formatting handler for assistant creation
  const handleAssistantPhoneChange = (value: string) => {
    setNewAssistant({ ...newAssistant, phone: formatPhoneNumber(value) });
  };

  const handleAssignClient = async () => {
    if (!selectedClient || !assignmentAssistant) return;
    
    try {
      const endpoint = assignmentType === 'primary' 
        ? `/api/v1/management/clients/${selectedClient.id}/assign-primary-assistant`
        : `/api/v1/management/clients/${selectedClient.id}/assign-additional-assistant`;
        
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ assistant_id: assignmentAssistant })
      });
      
      if (response.ok) {
        const result = await response.json();
        const assignmentTypeText = assignmentType === 'primary' ? 'главным ассистентом' : 'дополнительным ассистентом';
        setError(`Клиент успешно закреплен за ${assignmentTypeText}! Назначено задач: ${result.assigned_tasks}`);
        setAssignClientDialogOpen(false);
        setSelectedClient(null);
        setAssignmentAssistant(null);
        setAssignmentType('primary');
        await loadClients(); // Refresh clients
        await loadAssistants(); // Refresh assistants to update their task counts
        setTimeout(() => setError(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка назначения клиента');
      }
    } catch (error) {
      console.error('Ошибка назначения клиента:', error);
      setError(error instanceof Error ? error.message : 'Ошибка назначения клиента');
    }
  };

  const handleUnassignClient = async (client: Client) => {
    try {
      const confirmUnassign = window.confirm(
        `Вы уверены, что хотите отменить назначение ассистента для клиента "${client.name}"? Все активные задачи вернутся в маркетплейс.`
      );
      
      if (!confirmUnassign) return;
      
      // Get the assignment ID from the client's assigned assistants
      const assignment = client.assigned_assistants?.[0];
      if (!assignment) {
        throw new Error('Не найдено назначение для отмены');
      }
      
      const response = await fetch(`${API_BASE_URL}/api/v1/management/assignments/${assignment.assignment_id}/deactivate`, {
        method: 'PUT',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const result = await response.json();
        setError(`Назначение ассистента отменено! ${result.message}`);
        await loadClients(); // Refresh clients
        await loadAssistants(); // Refresh assistants to update their task counts
        setTimeout(() => setError(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка отмены назначения');
      }
    } catch (error) {
      console.error('Ошибка отмены назначения:', error);
      setError(error instanceof Error ? error.message : 'Ошибка отмены назначения');
    }
  };

  const openAssignClientDialog = async (client: Client) => {
    setSelectedClient(client);
    await loadAvailableAssistants('personal'); // Load available assistants for general assignment
    setAssignClientDialogOpen(true);
  };

  const handleResetPassword = async (assistantId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/management/assistants/${assistantId}/reset-password`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        const result = await response.json();
        setNewPassword(result.new_password);
        setResetPasswordDialogOpen(true);
        setError(`Пароль успешно сброшен!`);
        setTimeout(() => setError(null), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка сброса пароля');
      }
    } catch (error) {
      console.error('Ошибка сброса пароля:', error);
      setError(error instanceof Error ? error.message : 'Ошибка сброса пароля');
    }
  };

  // Filter and paginate clients (API уже возвращает только клиентов с активными подписками по умолчанию)
  const filteredClients = clients.filter(client => {
    const matchesFilter = client.name.toLowerCase().includes(clientFilter.toLowerCase()) ||
                         client.phone.toLowerCase().includes(clientFilter.toLowerCase()) ||
                         (client.email && client.email.toLowerCase().includes(clientFilter.toLowerCase()));
    
    return matchesFilter;
  });

  const paginatedClients = filteredClients.slice(
    clientPage * clientRowsPerPage,
    clientPage * clientRowsPerPage + clientRowsPerPage
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ background: managerGradients.header }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'white', fontWeight: 600 }}>
            📊 Панель управления: {manager?.name}
          </Typography>
          <IconButton color="inherit" onClick={logout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert 
            severity={error.includes('успешно') || error.includes('successful') ? "success" : "error"} 
            sx={{ mb: 3 }} 
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* Tabs */}
        <EnhancedPaper sx={{ mb: 3 }}>
          <Tabs 
            value={currentTab} 
            onChange={(_, newValue) => setCurrentTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
            sx={{ px: 2 }}
          >
            <Tab 
              icon={<DashboardIcon />} 
              label="Обзор" 
              sx={{ fontWeight: 500 }}
            />
            <Tab 
              icon={<TaskIcon />} 
              label="Задачи" 
              sx={{ fontWeight: 500 }}
            />
            <Tab 
              icon={<PeopleIcon />} 
              label="Ассистенты" 
              sx={{ fontWeight: 500 }}
            />
            <Tab 
              icon={<PersonIcon />} 
              label="Клиенты" 
              sx={{ fontWeight: 500 }}
            />
          </Tabs>
        </EnhancedPaper>

        {/* Tab Content */}
        <Box sx={{ mt: 3 }}>
          {currentTab === 0 && renderOverviewTab()}
          {currentTab === 1 && renderTasksTab()}
          {currentTab === 2 && renderAssistantsTab()}
          {currentTab === 3 && renderClientsTab()}
        </Box>

        {/* Task Reassignment Dialog */}
        <Dialog 
          open={reassignDialogOpen} 
          onClose={() => setReassignDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Переназначить задачу: {selectedTask?.title}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Тип задачи: {selectedTask && getStatusText(selectedTask.type)}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Клиент: {selectedTask?.client.name}
              </Typography>
              
              {selectedTask?.assistant && (
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Текущий ассистент: {selectedTask.assistant.name}
                </Typography>
              )}

              <FormControl fullWidth sx={{ mt: 3 }}>
                <InputLabel>Выбрать ассистента</InputLabel>
                <Select
                  value={selectedAssistant || ''}
                  onChange={(e) => setSelectedAssistant(e.target.value as number)}
                  label="Выбрать ассистента"
                >
                  <MenuItem value="">
                    <em>Вернуть в маркетплейс</em>
                  </MenuItem>
                  {availableAssistants.map((assistant) => (
                    <MenuItem 
                      key={assistant.id} 
                      value={assistant.id}
                      disabled={!assistant.is_available}
                    >
                      <Box>
                        <Typography variant="body2">
                          {assistant.name} 
                          {!assistant.is_available && ' (недоступен)'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {getStatusText(assistant.specialization)} • 
                          {assistant.current_active_tasks}/5 задач • 
                          ★ {assistant.average_rating.toFixed(1)}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReassignDialogOpen(false)}>
              Отмена
            </Button>
            <Button 
              onClick={() => selectedTask && handleTaskReassign(selectedTask.id, selectedAssistant)}
              variant="contained"
            >
              Переназначить
            </Button>
          </DialogActions>
        </Dialog>

        {/* Create Assistant Dialog */}
        <Dialog
          open={createAssistantDialogOpen}
          onClose={() => setCreateAssistantDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Создать нового ассистента</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <TextField
                label="Имя ассистента"
                fullWidth
                margin="normal"
                value={newAssistant.name}
                onChange={(e) => setNewAssistant({ ...newAssistant, name: e.target.value })}
              />
              <TextField
                label="Email"
                fullWidth
                margin="normal"
                value={newAssistant.email}
                onChange={(e) => setNewAssistant({ ...newAssistant, email: e.target.value })}
              />
              <TextField
                label="Телефон"
                fullWidth
                margin="normal"
                value={newAssistant.phone}
                onChange={(e) => handleAssistantPhoneChange(e.target.value)}
                type="tel"
                autoComplete="tel"
                placeholder="+7 (999) 123-45-67"
                helperText={newAssistant.phone && !isValidPhoneNumber(newAssistant.phone) ? "Введите корректный номер телефона" : ""}
                error={newAssistant.phone !== '' && !isValidPhoneNumber(newAssistant.phone)}
              />
              <TextField
                label="Пароль"
                fullWidth
                margin="normal"
                type="password"
                value={newAssistant.password}
                onChange={(e) => setNewAssistant({ ...newAssistant, password: e.target.value })}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Специализация</InputLabel>
                <Select
                  value={newAssistant.specialization}
                  onChange={(e) => setNewAssistant({ ...newAssistant, specialization: e.target.value as string })}
                  label="Специализация"
                >
                  <MenuItem value="personal_only">Только личные задачи</MenuItem>
                  <MenuItem value="full_access">Полный доступ</MenuItem>
                  <MenuItem value="business_only">Только бизнес задачи</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="Telegram Username (опционально)"
                fullWidth
                margin="normal"
                value={newAssistant.telegram_username}
                onChange={(e) => setNewAssistant({ ...newAssistant, telegram_username: e.target.value })}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateAssistantDialogOpen(false)}>
              Отмена
            </Button>
            <Button 
              onClick={handleCreateAssistant}
              variant="contained"
              disabled={
                !newAssistant.name || 
                !newAssistant.phone || 
                !newAssistant.email || 
                !newAssistant.password || 
                !isValidPhoneNumber(newAssistant.phone)
              }
            >
              Создать ассистента
            </Button>
          </DialogActions>
        </Dialog>

        {/* Assistant Profile Dialog */}
        <Dialog
          open={assistantProfileDialogOpen}
          onClose={() => setAssistantProfileDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PersonIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Профиль ассистента: {selectedAssistantProfile?.name}
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedAssistantProfile && (
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={3}>
                  {/* Basic Information */}
                  <Grid item xs={12} md={6}>
                    <EnhancedPaper sx={{ p: 3 }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        Основная информация
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            ID ассистента
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            #{selectedAssistantProfile.id}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Полное имя
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedAssistantProfile.name}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Email
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedAssistantProfile.email}
                          </Typography>
                        </Box>
                        {selectedAssistantProfile.phone && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Телефон
                            </Typography>
                            <Typography variant="body1" fontWeight={500}>
                              {selectedAssistantProfile.phone}
                            </Typography>
                          </Box>
                        )}
                        {selectedAssistantProfile.telegram_username && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Telegram
                            </Typography>
                            <Typography variant="body1" fontWeight={500}>
                              {selectedAssistantProfile.telegram_username}
                            </Typography>
                          </Box>
                        )}
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Пароль
                            </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight={500} sx={{ 
                              fontFamily: 'monospace',
                              bgcolor: selectedAssistantProfile.last_known_password ? 'success.50' : 'grey.100',
                              color: selectedAssistantProfile.last_known_password ? 'success.main' : 'text.disabled',
                              p: 1,
                              borderRadius: 1,
                              border: '1px solid',
                              borderColor: selectedAssistantProfile.last_known_password ? 'success.main' : 'grey.300'
                            }}>
                              {selectedAssistantProfile.last_known_password || 'Неизвестен'}
                            </Typography>
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleResetPassword(selectedAssistantProfile.id)}
                              sx={{ minWidth: 'auto' }}
                            >
                              Сбросить
                            </Button>
                          </Box>
                          {selectedAssistantProfile.last_password_reset_at && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                              Последний сброс: {new Date(selectedAssistantProfile.last_password_reset_at).toLocaleString('ru-RU')}
                            </Typography>
                        )}
                        </Box>
                      </Box>
                    </EnhancedPaper>
                  </Grid>
                  
                  {/* Performance Information */}
                  <Grid item xs={12} md={6}>
                    <EnhancedPaper sx={{ p: 3 }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        Показатели эффективности
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Специализация
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {getStatusText(selectedAssistantProfile.specialization)}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Статус
                          </Typography>
                          <Typography variant="body1" fontWeight={500} color={
                            selectedAssistantProfile.status === 'online' ? 'success.main' : 'text.secondary'
                          }>
                            {selectedAssistantProfile.status === 'online' ? 'В сети' : 'Не в сети'}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Активные задачи
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedAssistantProfile.current_active_tasks}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Выполнено задач
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedAssistantProfile.total_tasks_completed}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Рейтинг
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            ★ {selectedAssistantProfile.average_rating.toFixed(1)}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Загрузка
                          </Typography>
                          <Typography variant="body1" fontWeight={500} color={
                            selectedAssistantProfile.current_active_tasks >= 5 ? 'error.main' : 
                            selectedAssistantProfile.current_active_tasks >= 3 ? 'warning.main' : 'success.main'
                          }>
                            {selectedAssistantProfile.current_active_tasks}/5 задач ({Math.round((selectedAssistantProfile.current_active_tasks / 5) * 100)}%)
                          </Typography>
                        </Box>
                      </Box>
                    </EnhancedPaper>
                  </Grid>
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAssistantProfileDialogOpen(false)}>
              Закрыть
            </Button>
          </DialogActions>
        </Dialog>

        {/* Assign Client Dialog */}
        <Dialog
          open={assignClientDialogOpen}
          onClose={() => setAssignClientDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Назначить клиента ассистенту</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Клиент: {selectedClient?.name}
              </Typography>
              
              {/* Show current assignments */}
              {selectedClient?.assigned_assistants && selectedClient.assigned_assistants.length > 0 && (
                <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Текущие назначения:</strong>
                    <br />
                    {selectedClient.assigned_assistants.map((assistant, index) => (
                      <span key={assistant.id}>
                        {assistant.name} ({assistant.specialization})
                        {index < selectedClient.assigned_assistants!.length - 1 && ', '}
                      </span>
                    ))}
                  </Typography>
                </Alert>
              )}
              
              {/* Show multiple assignment info */}
              <Box sx={{ p: 2, bgcolor: 'success.50', borderRadius: 2, border: '1px solid', borderColor: 'success.200', mb: 2 }}>
                <Typography variant="body2" color="success.main">
                  <InfoIcon sx={{ mr: 1, fontSize: 16, verticalAlign: 'middle' }} />
                  Система поддерживает назначение нескольких ассистентов на одного клиента. 
                  Новые задачи будут доступны всем назначенным ассистентам.
                </Typography>
              </Box>
              
              <FormControl fullWidth margin="normal">
                <InputLabel>Выбрать ассистента</InputLabel>
                <Select
                  value={assignmentAssistant || ''}
                  onChange={(e) => setAssignmentAssistant(e.target.value as number)}
                  label="Выбрать ассистента"
                >
                  <MenuItem value="">
                    <em>Выберите ассистента</em>
                  </MenuItem>
                  {availableAssistants.map((assistant) => (
                    <MenuItem 
                      key={assistant.id} 
                      value={assistant.id}
                      disabled={!assistant.is_available}
                    >
                      <Box>
                        <Typography variant="body2">
                          {assistant.name} 
                          {!assistant.is_available && ' (недоступен)'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {getStatusText(assistant.specialization)} • 
                          {assistant.current_active_tasks}/5 задач • 
                          ★ {assistant.average_rating.toFixed(1)}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAssignClientDialogOpen(false)}>
              Отмена
            </Button>
            <Button 
              onClick={handleAssignClient}
              variant="contained"
              color="primary"
            >
              Назначить ассистента
            </Button>
          </DialogActions>
        </Dialog>

        {/* Password Reset Dialog */}
        <Dialog
          open={resetPasswordDialogOpen}
          onClose={() => setResetPasswordDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <InfoIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Новый пароль создан
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Пароль успешно сброшен! Сообщите новый пароль ассистенту.
                </Typography>
              </Alert>
              
              <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, border: '1px solid', borderColor: 'grey.300' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Новый пароль:
                </Typography>
                <Typography variant="h6" fontWeight="bold" sx={{ 
                  fontFamily: 'monospace',
                  bgcolor: 'primary.50',
                  p: 2,
                  borderRadius: 1,
                  border: '2px solid',
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  textAlign: 'center'
                }}>
                  {newPassword}
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2, p: 2, bgcolor: 'warning.50', borderRadius: 2, border: '1px solid', borderColor: 'warning.200' }}>
                <Typography variant="body2" color="warning.main">
                  <WarningIcon sx={{ mr: 1, fontSize: 16, verticalAlign: 'middle' }} />
                  Скопируйте этот пароль сейчас! Он не будет показан повторно.
                </Typography>
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => navigator.clipboard.writeText(newPassword)}
              variant="outlined"
              color="primary"
            >
              Скопировать пароль
            </Button>
            <Button onClick={() => setResetPasswordDialogOpen(false)} variant="contained">
              Закрыть
            </Button>
          </DialogActions>
        </Dialog>

        {/* Client Profile Dialog */}
        <Dialog
          open={clientProfileDialogOpen}
          onClose={() => setClientProfileDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PersonIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Профиль клиента: {selectedClientProfile?.name}
              </Typography>
            </Box>
          </DialogTitle>
          <DialogContent>
            {selectedClientProfile && (
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={3}>
                  {/* Basic Information */}
                  <Grid item xs={12} md={6}>
                    <EnhancedPaper sx={{ p: 3 }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        Личная информация
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            ID клиента
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            #{selectedClientProfile.id}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Полное имя
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedClientProfile.name}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Номер телефона
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {selectedClientProfile.phone}
                          </Typography>
                        </Box>
                        {selectedClientProfile.email && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Email
                            </Typography>
                            <Typography variant="body1" fontWeight={500}>
                              {selectedClientProfile.email}
                            </Typography>
                          </Box>
                        )}
                        {selectedClientProfile.telegram_username && (
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Telegram алиас
                            </Typography>
                            <Typography variant="body1" fontWeight={500}>
                              @{selectedClientProfile.telegram_username}
                            </Typography>
                          </Box>
                        )}
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Дата регистрации
                          </Typography>
                          <Typography variant="body1" fontWeight={500}>
                            {new Date(selectedClientProfile.created_at).toLocaleDateString('ru-RU', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </Typography>
                        </Box>
                      </Box>
                    </EnhancedPaper>
                  </Grid>
                  
                  {/* Subscription Information */}
                  <Grid item xs={12} md={6}>
                    <EnhancedPaper sx={{ p: 3 }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        Информация о подписке
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {selectedClientProfile.subscription ? (
                          <>
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Тип подписки
                              </Typography>
                              <Typography variant="body1" fontWeight={500}>
                                {getSubscriptionPlanName(selectedClientProfile.subscription.plan)}
                              </Typography>
                            </Box>
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Статус
                              </Typography>
                              <Typography variant="body1" fontWeight={500} color={
                                selectedClientProfile.subscription.status === 'active' ? 'success.main' : 'text.secondary'
                              }>
                                {getStatusText(selectedClientProfile.subscription.status)}
                              </Typography>
                            </Box>
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Начало подписки
                              </Typography>
                              <Typography variant="body1" fontWeight={500}>
                                {new Date(selectedClientProfile.subscription.started_at).toLocaleDateString('ru-RU')}
                              </Typography>
                            </Box>
                            {selectedClientProfile.subscription.expires_at && (
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  Окончание подписки
                                </Typography>
                                <Typography variant="body1" fontWeight={500}>
                                  {new Date(selectedClientProfile.subscription.expires_at).toLocaleDateString('ru-RU')}
                                </Typography>
                              </Box>
                            )}
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Автопродление
                              </Typography>
                              <Typography variant="body1" fontWeight={500}>
                                {selectedClientProfile.subscription.auto_renew ? 'Включено' : 'Отключено'}
                              </Typography>
                            </Box>
                          </>
                        ) : (
                          <Box sx={{ textAlign: 'center', py: 2 }}>
                            <Typography variant="body1" color="text.secondary">
                              У клиента нет активной подписки
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </EnhancedPaper>
                  </Grid>

                  {/* Task Statistics */}
                  <Grid item xs={12}>
                    <EnhancedPaper sx={{ p: 3 }}>
                      <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
                        Статистика задач
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={6} md={3}>
                          <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'primary.50', borderRadius: 2 }}>
                            <Typography variant="h5" fontWeight="bold" color="primary.main">
                              {selectedClientProfile.total_tasks}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Всего задач
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'warning.50', borderRadius: 2 }}>
                            <Typography variant="h5" fontWeight="bold" color="warning.main">
                              {selectedClientProfile.active_tasks}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Активных задач
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'success.50', borderRadius: 2 }}>
                            <Typography variant="h5" fontWeight="bold" color="success.main">
                              {selectedClientProfile.total_tasks - selectedClientProfile.active_tasks}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Завершено
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6} md={3}>
                          <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'info.50', borderRadius: 2 }}>
                            <Typography variant="h5" fontWeight="bold" color="info.main">
                              {selectedClientProfile.assigned_assistants?.length || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Ассистентов
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </EnhancedPaper>
                  </Grid>
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setClientProfileDialogOpen(false)}>
              Закрыть
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default Dashboard; 