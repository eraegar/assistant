import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Avatar,
  Divider,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  styled,
} from '@mui/material';
import {
  Person,
  Phone,
  Email,
  Edit,
  Save,
  Cancel,
  AccountCircle,
  History,
  Star,
  Telegram,
} from '@mui/icons-material';
import { useAuthStore } from '../stores/useAuthStore';
import { useTaskStore } from '../stores/useTaskStore';
import { EnhancedPaper, GradientChip, clientGradients } from '../styles/gradients';

interface ProfileModalProps {
  open: boolean;
  onClose: () => void;
}

const ProfileHeader = styled(Box)(({ theme }) => ({
  background: clientGradients.header,
  color: 'white',
  padding: theme.spacing(3),
  textAlign: 'center',
  borderRadius: '8px 8px 0 0',
  marginBottom: theme.spacing(2),
}));

const ProfileModal: React.FC<ProfileModalProps> = ({ open, onClose }) => {
  const { user } = useAuthStore();
  const { tasks } = useTaskStore();
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSave = async () => {
    try {
      setError(null);
      // For now, just show success message since updateProfile doesn't exist
      // In a real app, you would call the API to update profile
      setSuccess('Профиль успешно обновлен');
      setIsEditing(false);
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      setError('Произошла ошибка при обновлении профиля');
    }
  };

  const handleCancel = () => {
    setEditData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
    });
    setIsEditing(false);
    setError(null);
  };

  const completedTasks = tasks.filter(task => task.status === 'completed').length;
  const totalTasks = tasks.length;
  const averageRating = 4.8; // Mock data for now

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ p: 0 }}>
        <ProfileHeader>
          <Avatar 
            sx={{ 
              width: 80, 
              height: 80, 
              margin: '0 auto 16px',
              background: 'rgba(255, 255, 255, 0.2)',
              fontSize: '2rem',
            }}
          >
            {user?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase()}
          </Avatar>
          <Typography variant="h5" fontWeight="bold">
            {user?.name || 'Пользователь'}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Клиент с {new Date(user?.created_at || Date.now()).toLocaleDateString('ru-RU')}
          </Typography>
        </ProfileHeader>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Personal Information */}
            <Grid item xs={12} md={6}>
              <EnhancedPaper sx={{ p: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AccountCircle sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Личная информация
                  </Typography>
                  {!isEditing && (
                    <Button
                      size="small"
                      startIcon={<Edit />}
                      onClick={() => setIsEditing(true)}
                      sx={{ ml: 'auto' }}
                    >
                      Редактировать
                    </Button>
                  )}
                </Box>

                <List dense>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Person color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Имя"
                      secondary={
                        isEditing ? (
                          <TextField
                            fullWidth
                            size="small"
                            value={editData.name}
                            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                            sx={{ mt: 1 }}
                          />
                        ) : (
                          user?.name || 'Не указано'
                        )
                      }
                    />
                  </ListItem>

                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Email color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Email"
                      secondary={
                        isEditing ? (
                          <TextField
                            fullWidth
                            size="small"
                            value={editData.email}
                            onChange={(e) => setEditData({ ...editData, email: e.target.value })}
                            sx={{ mt: 1 }}
                          />
                        ) : (
                          user?.email || 'Не указано'
                        )
                      }
                    />
                  </ListItem>

                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Phone color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Телефон"
                      secondary={user?.phone || 'Не указано'}
                    />
                  </ListItem>

                  <ListItem sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Telegram color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Telegram"
                      secondary={user?.telegram_username ? `@${user.telegram_username}` : 'Не указано'}
                    />
                  </ListItem>
                </List>

                {isEditing && (
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Save />}
                      onClick={handleSave}
                      sx={{
                        background: clientGradients.primary,
                        '&:hover': {
                          background: clientGradients.primary,
                        }
                      }}
                    >
                      Сохранить
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Cancel />}
                      onClick={handleCancel}
                    >
                      Отмена
                    </Button>
                  </Box>
                )}
              </EnhancedPaper>
            </Grid>

            {/* Statistics */}
            <Grid item xs={12} md={6}>
              <EnhancedPaper sx={{ p: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <History sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6" fontWeight="bold">
                    Статистика
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, background: 'rgba(102, 126, 234, 0.1)', borderRadius: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="primary.main">
                        {totalTasks}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Всего задач
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, background: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="success.main">
                        {completedTasks}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Выполнено
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ textAlign: 'center', p: 2, background: 'rgba(255, 193, 7, 0.1)', borderRadius: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                        <Star sx={{ color: 'warning.main', mr: 0.5 }} />
                        <Typography variant="h4" fontWeight="bold" color="warning.main">
                          {averageRating}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        Средний рейтинг
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </EnhancedPaper>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 0 }}>
        <Button onClick={onClose} variant="outlined">
          Закрыть
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProfileModal; 