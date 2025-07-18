import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { User, Task, TaskType, TaskStatus, TaskApproval, TaskRevision, ApiResponse } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = process.env.NODE_ENV === 'production' ? 'https://api.rent-assistant.ru/api/v1' : 'http://127.0.0.1:8000/api/v1';

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth interceptor
    this.api.interceptors.request.use((config) => {
      const token = this.getAuthToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.removeAuthToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  private setAuthToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  private removeAuthToken(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  private saveUserData(userData: User): void {
    localStorage.setItem('user_data', JSON.stringify(userData));
  }

  public getUserData(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  // Auth endpoints
  async login(phone: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      const response = await this.api.post('/clients/auth/login', { phone, password });
      const { access_token } = response.data;
      
      this.setAuthToken(access_token);
      
      // Get user profile
      const profileResponse = await this.api.get('/clients/profile');
      const user = profileResponse.data;
      
      this.saveUserData(user);
      
      return {
        success: true,
        data: { user, token: access_token }
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async register(name: string, phone: string, password: string, telegram_username?: string): Promise<ApiResponse<{ user: User; token: string }>> {
    try {
      await this.api.post('/clients/auth/register', {
        name,
        phone,
        password,
        telegram_username
      });
      
      // Auto-login after registration
      return await this.login(phone, password);
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async logout(): Promise<void> {
    this.removeAuthToken();
  }

  // Profile endpoints
  async getProfile(): Promise<ApiResponse<User>> {
    try {
      const response = await this.api.get('/clients/profile');
      this.saveUserData(response.data);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  // Task endpoints
  async getTasks(): Promise<ApiResponse<Task[]>> {
    try {
      const response = await this.api.get('/clients/tasks');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message,
        data: []
      };
    }
  }

  async getTask(taskId: string): Promise<ApiResponse<Task>> {
    try {
      const response = await this.api.get(`/clients/tasks/${taskId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async createTask(title: string, description: string, type: TaskType): Promise<ApiResponse<Task>> {
    try {
      const response = await this.api.post('/clients/tasks', {
        title,
        description,
        type: type.toLowerCase() // Ensure enum name is lowercase to match backend
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      console.error('Create task API error:', error.response?.data || error.message);
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async updateTaskStatus(taskId: string, status: TaskStatus, result?: string): Promise<ApiResponse> {
    try {
      const response = await this.api.put(`/clients/tasks/${taskId}`, {
        status,
        ...(result && { result })
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  // Новые методы для работы с оценкой и доработкой задач
  async approveTask(taskId: string, approval: TaskApproval): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/clients/tasks/${taskId}/approve`, approval);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async requestRevision(taskId: string, revision: TaskRevision): Promise<ApiResponse> {
    try {
      const response = await this.api.post(`/clients/tasks/${taskId}/request-revision`, revision);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  // Subscription endpoints
  async getSubscriptionPlans(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.api.get('/clients/subscription/plans');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message,
        data: []
      };
    }
  }

  async getTaskTypePermissions(): Promise<ApiResponse<{
    allowed_types: string[];
    plan_type: string;
    subscription_plan: string;
    can_choose_type: boolean;
    message: string;
  }>> {
    try {
      const response = await this.api.get('/clients/subscription/task-types');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message,
        data: {
          allowed_types: [],
          plan_type: 'none',
          subscription_plan: 'none',
          can_choose_type: false,
          message: 'No subscription found'
        }
      };
    }
  }

  async upgradeSubscription(planType: string, paymentToken: string): Promise<ApiResponse> {
    try {
      console.log('🔄 Upgrading subscription:', { planType, paymentToken });
      
      const response = await this.api.post('/clients/subscription/upgrade', {
        plan: planType,
        payment_token: paymentToken
      });
      
      console.log('✅ Subscription upgrade response:', response.data);
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      console.error('❌ Subscription upgrade error:', error.response?.data || error.message);
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async cancelSubscription(): Promise<ApiResponse> {
    try {
      const response = await this.api.post('/clients/subscription/cancel');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }

  async getSubscriptionStatus(): Promise<ApiResponse<any>> {
    try {
      const response = await this.api.get('/clients/subscription/status');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || error.message
      };
    }
  }
}

export const apiService = new ApiService(); 