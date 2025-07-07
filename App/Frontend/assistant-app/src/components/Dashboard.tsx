import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
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
  Paper,
  Chip,
  IconButton,
  AppBar,
  Toolbar,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  styled,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assignment as TaskIcon,
  Store as MarketplaceIcon,
  Logout as LogoutIcon,
  CheckCircle as CompleteIcon,
  PlayArrow as ClaimIcon,
  Star as StarIcon,
  AccessTime as TimeIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  Cancel as RejectIcon,
} from '@mui/icons-material';
import { useAssistantStore } from '../stores/useAssistantStore';
import { assistantGradients } from '../theme';

// API base URL
const API_BASE_URL = 'https://api.rent-assistant.ru';

// Styled components for enhanced design
const StatsCard = styled(Card)(({ theme }) => ({
  background: assistantGradients.card,
  borderRadius: 16,
  transition: 'all 0.3s ease-in-out',
  border: '1px solid rgba(46, 125, 50, 0.1)',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 40px rgba(46, 125, 50, 0.15)',
  },
}));

const EnhancedPaper = styled(Paper)(({ theme }) => ({
  borderRadius: 16,
  background: assistantGradients.card,
  border: '1px solid rgba(46, 125, 50, 0.08)',
}));

const GradientChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  fontWeight: 500,
  '&.MuiChip-colorPrimary': {
    background: assistantGradients.primary,
  },
  '&.MuiChip-colorSecondary': {
    background: assistantGradients.secondary,
  },
  '&.MuiChip-colorSuccess': {
    background: assistantGradients.success,
  },
}));

interface MarketplaceTask {
  id: number;
  title: string;
  description: string;
  type: string;
  client_name: string;
  created_at: string;
  deadline?: string;
  time_remaining: string;
}

interface AssignedTask {
  id: number;
  title: string;
  description: string;
  type: string;
  status: string;
  created_at: string;
  deadline?: string;
  claimed_at?: string;
  completed_at?: string;
  result?: string;
  completion_notes?: string;
  client_rating?: number;
  client_feedback?: string;
}

interface DashboardStats {
  total_tasks: number;
  active_tasks: number;
  completed_tasks: number;
  average_rating: number;
  available_marketplace_tasks: number;
  status: string;
  specialization: string;
}

const Dashboard: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [marketplaceTasks, setMarketplaceTasks] = useState<MarketplaceTask[]>([]);
  const [assignedTasks, setAssignedTasks] = useState<AssignedTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Complete task dialog
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [taskResult, setTaskResult] = useState('');
  const [completionNotes, setCompletionNotes] = useState('');
  
  // Reject task dialog
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  
  const { assistant, logout, updateStatus } = useAssistantStore();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('assistant_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadStats(),
        loadMarketplaceTasks(),
        loadAssignedTasks()
      ]);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/assistants/dashboard/stats`, {
      headers: getAuthHeaders()
    });
    if (response.ok) {
      const data = await response.json();
      setStats(data);
    }
  };

  const loadMarketplaceTasks = async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/assistants/tasks/marketplace?limit=20`, {
      headers: getAuthHeaders()
    });
    if (response.ok) {
      const data = await response.json();
      setMarketplaceTasks(data);
    }
  };

  const loadAssignedTasks = async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/assistants/tasks/assigned?limit=20`, {
      headers: getAuthHeaders()
    });
    if (response.ok) {
      const data = await response.json();
      setAssignedTasks(data);
    }
  };

  const handleStatusToggle = async (checked: boolean) => {
    const newStatus = checked ? 'online' : 'offline';
    const success = await updateStatus(newStatus);
    if (success) {
      await loadStats();
    }
  };

  const claimTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/assistants/tasks/${taskId}/claim`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      if (response.ok) {
        await loadDashboardData(); // Refresh all data
      } else {
        setError('Не удалось взять задачу');
      }
    } catch (error) {
      setError('Ошибка при получении задачи');
    }
  };

  const handleCompleteTask = (taskId: number) => {
    setSelectedTaskId(taskId);
    setCompleteDialogOpen(true);
  };

  const submitTaskCompletion = async () => {
    if (!selectedTaskId || !taskResult.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/assistants/tasks/${selectedTaskId}/complete`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          detailed_result: taskResult,
          completion_summary: completionNotes
        })
      });

      if (response.ok) {
        setCompleteDialogOpen(false);
        setTaskResult('');
        setCompletionNotes('');
        setSelectedTaskId(null);
        await loadDashboardData();
      } else {
        setError('Не удалось завершить задачу');
      }
    } catch (error) {
      setError('Ошибка при завершении задачи');
    }
  };

  const handleRejectTask = (taskId: number) => {
    setSelectedTaskId(taskId);
    setRejectDialogOpen(true);
  };

  const submitTaskRejection = async () => {
    if (!selectedTaskId || !rejectReason.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/assistants/tasks/${selectedTaskId}/reject`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          reason: rejectReason
        })
      });

      if (response.ok) {
        setRejectDialogOpen(false);
        setRejectReason('');
        setSelectedTaskId(null);
        await loadDashboardData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Не удалось отклонить задачу');
      }
    } catch (error) {
      setError('Ошибка при отклонении задачи');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'in_progress': return 'info';
      case 'completed': return 'success';
      case 'approved': return 'success';
      case 'revision_requested': return 'warning';
      case 'rejected': return 'error';
      case 'cancelled': return 'secondary';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      'pending': 'Ожидает',
      'in_progress': 'В работе',
      'completed': 'Завершена',
      'approved': 'Одобрена',
      'revision_requested': 'Нужны исправления',
      'rejected': 'Отклонена',
      'cancelled': 'Отменена',
      'personal': 'Личное',
      'business': 'Бизнес'
    };
    return statusMap[status] || status;
  };

  const renderStatsTab = () => {
    if (!stats) return <CircularProgress />;

    return (
      <Box>
        {/* Welcome Section */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            Добро пожаловать, {assistant?.name}! 🌟
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Ваша рабочая панель ассистента
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <StatsCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TaskIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Активные задачи
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.active_tasks}
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
                  <CompleteIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Выполнено
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.completed_tasks}
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
                  <StarIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Средний рейтинг
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.average_rating}⭐
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
                  <MarketplaceIcon color="secondary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2" fontWeight={500}>
                      Доступно задач
                    </Typography>
                    <Typography variant="h4" fontWeight="bold">
                      {stats.available_marketplace_tasks}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </StatsCard>
          </Grid>

          <Grid item xs={12}>
            <EnhancedPaper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Информация профиля
              </Typography>
              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Специализация
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {getStatusText(stats.specialization)}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUpIcon sx={{ mr: 1, color: 'success.main' }} />
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Всего задач
                      </Typography>
                      <Typography variant="body1" fontWeight={500}>
                        {stats.total_tasks}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ mr: 1 }}>
                      <GradientChip 
                        label={stats.status === 'online' ? 'В сети' : 'Не в сети'} 
                        color={stats.status === 'online' ? 'success' : 'secondary'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Текущий статус
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

  const renderMarketplaceTab = () => {
    return (
      <Box>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight="bold">
            Рынок задач ({marketplaceTasks.length})
          </Typography>
          <Button 
            variant="outlined" 
            onClick={loadMarketplaceTasks}
            startIcon={<RefreshIcon />}
          >
            Обновить
          </Button>
        </Box>

        <TableContainer component={EnhancedPaper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Задача</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Тип</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Клиент</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Дедлайн</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {marketplaceTasks.map((task) => (
                <TableRow key={task.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {task.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {task.description.substring(0, 100)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <GradientChip 
                      label={getStatusText(task.type)} 
                      color="primary" 
                      variant="outlined" 
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {task.client_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <TimeIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2">
                        {task.time_remaining}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Button
                      startIcon={<ClaimIcon />}
                      variant="contained"
                      size="small"
                      onClick={() => claimTask(task.id)}
                    >
                      Взять
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  const renderMyTasksTab = () => {
    return (
      <Box>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontWeight="bold">
            Мои задачи ({assignedTasks.length})
          </Typography>
          <Button 
            variant="outlined" 
            onClick={loadAssignedTasks}
            startIcon={<RefreshIcon />}
          >
            Обновить
          </Button>
        </Box>

        <TableContainer component={EnhancedPaper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Задача</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Статус</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Дата взятия</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Оценка</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {assignedTasks.map((task) => (
                <TableRow key={task.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {task.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {task.description.substring(0, 100)}...
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <GradientChip 
                      label={getStatusText(task.status)} 
                      color={getStatusColor(task.status)} 
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {task.claimed_at ? new Date(task.claimed_at).toLocaleDateString('ru-RU') : '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {task.client_rating ? (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <StarIcon sx={{ color: 'gold', mr: 0.5, fontSize: 18 }} />
                        <Typography variant="body2" fontWeight={500}>
                          {task.client_rating}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        -
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {(task.status === 'in_progress' || task.status === 'revision_requested') && (
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          startIcon={<CompleteIcon />}
                          variant="contained"
                          size="small"
                          color="success"
                          onClick={() => handleCompleteTask(task.id)}
                        >
                          {task.status === 'revision_requested' ? 'Исправить и завершить' : 'Завершить'}
                        </Button>
                        <Button
                          startIcon={<RejectIcon />}
                          variant="outlined"
                          size="small"
                          color="warning"
                          onClick={() => handleRejectTask(task.id)}
                        >
                          Отклонить
                        </Button>
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ background: assistantGradients.header }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'white', fontWeight: 600 }}>
            🔧 Рабочее место: {assistant?.name}
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={stats?.status === 'online'}
                onChange={(e) => handleStatusToggle(e.target.checked)}
                color="default"
              />
            }
            label={stats?.status === 'online' ? 'В сети' : 'Не в сети'}
            sx={{ mr: 2, color: 'white' }}
          />
          
          <IconButton color="inherit" onClick={logout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
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
              label="Статистика" 
              sx={{ fontWeight: 500 }}
            />
            <Tab 
              icon={
                <Badge badgeContent={marketplaceTasks.length} color="secondary">
                  <MarketplaceIcon />
                </Badge>
              } 
              label="Рынок задач" 
              sx={{ fontWeight: 500 }}
            />
            <Tab 
              icon={
                <Badge badgeContent={assignedTasks.filter(t => t.status === 'in_progress' || t.status === 'revision_requested').length} color="primary">
                  <TaskIcon />
                </Badge>
              } 
              label="Мои задачи" 
              sx={{ fontWeight: 500 }}
            />
          </Tabs>
        </EnhancedPaper>

        {/* Tab Content */}
        <Box sx={{ mt: 3 }}>
          {currentTab === 0 && renderStatsTab()}
          {currentTab === 1 && renderMarketplaceTab()}
          {currentTab === 2 && renderMyTasksTab()}
        </Box>
      </Container>

      {/* Complete Task Dialog */}
      <Dialog 
        open={completeDialogOpen} 
        onClose={() => setCompleteDialogOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ fontWeight: 'bold' }}>
          Завершение задачи
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Результат выполнения"
            value={taskResult}
            onChange={(e) => setTaskResult(e.target.value)}
            margin="normal"
            required
            placeholder="Опишите подробно, что было сделано..."
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Дополнительные заметки (опционально)"
            value={completionNotes}
            onChange={(e) => setCompletionNotes(e.target.value)}
            margin="normal"
            placeholder="Любые дополнительные комментарии..."
          />
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setCompleteDialogOpen(false)} variant="outlined">
            Отмена
          </Button>
          <Button 
            onClick={submitTaskCompletion}
            variant="contained"
            disabled={!taskResult.trim()}
            startIcon={<CompleteIcon />}
          >
            Завершить задачу
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reject Task Dialog */}
      <Dialog 
        open={rejectDialogOpen} 
        onClose={() => setRejectDialogOpen(false)} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ fontWeight: 'bold', color: 'warning.main' }}>
          Отклонение задачи
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Пожалуйста, укажите причину отклонения задачи. Задача будет возвращена в общую биржу задач.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Причина отклонения"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            margin="normal"
            required
            placeholder="Опишите, почему вы не можете выполнить эту задачу..."
          />
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setRejectDialogOpen(false)} variant="outlined">
            Отмена
          </Button>
          <Button 
            onClick={submitTaskRejection}
            variant="contained"
            color="warning"
            disabled={!rejectReason.trim()}
            startIcon={<RejectIcon />}
          >
            Отклонить задачу
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard; 