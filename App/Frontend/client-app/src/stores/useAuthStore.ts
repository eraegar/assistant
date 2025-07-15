import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserStatus, AuthState } from '../types';
import { apiService } from '../services/api';
import { useTaskStore } from './useTaskStore';

interface AuthStore extends AuthState {
  login: (phone: string, password: string) => Promise<boolean>;
  register: (name: string, phone: string, password: string, telegram_username?: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  activateSubscription: (planType: string, paymentToken: string) => Promise<boolean>;
  setLoading: (loading: boolean) => void;
  determineUserStatus: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      userStatus: UserStatus.UNAUTHENTICATED,
      isLoading: false,
      token: null,

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      determineUserStatus: () => {
        const { user } = get();
        if (!user) {
          set({ userStatus: UserStatus.UNAUTHENTICATED });
        } else if (user.subscription?.status === 'active') {
          set({ userStatus: UserStatus.HAS_ACTIVE_SUBSCRIPTION });
        } else {
          set({ userStatus: UserStatus.NEEDS_SUBSCRIPTION });
        }
      },

      login: async (phone: string, password: string): Promise<boolean> => {
        set({ isLoading: true });
        try {
          const response = await apiService.login(phone, password);
          if (response.success && response.data) {
            set({ 
              user: response.data.user,
              token: response.data.token,
              isLoading: false
            });
            get().determineUserStatus();
            return true;
          }
          set({ isLoading: false });
          return false;
        } catch (error) {
          console.error('Login error:', error);
          set({ isLoading: false });
          return false;
        }
      },

      register: async (name: string, phone: string, password: string, telegram_username?: string): Promise<boolean> => {
        set({ isLoading: true });
        try {
          const response = await apiService.register(name, phone, password, telegram_username);
          if (response.success && response.data) {
            set({ 
              user: response.data.user,
              token: response.data.token,
              isLoading: false
            });
            get().determineUserStatus();
            return true;
          }
          set({ isLoading: false });
          return false;
        } catch (error) {
          console.error('Register error:', error);
          set({ isLoading: false });
          return false;
        }
      },

      logout: () => {
        // Remove tokens and persisted auth storage
        apiService.logout();
        localStorage.removeItem('auth-storage');

        // Clear tasks from TaskStore
        useTaskStore.setState({ tasks: [] });

        set({
          user: null,
          token: null,
          userStatus: UserStatus.UNAUTHENTICATED
        });

        // Redirect to landing page so components with protected data unmount
        // Force full page reload to stop all running effects/timers
        window.location.reload();
      },

      refreshUser: async () => {
        try {
          const response = await apiService.getProfile();
          if (response.success && response.data) {
            set({ user: response.data });
            get().determineUserStatus();
          }
        } catch (error) {
          console.error('Refresh user error:', error);
        }
      },

      activateSubscription: async (planType: string, paymentToken: string): Promise<boolean> => {
        set({ isLoading: true });
        try {
          console.log('🔄 Activating subscription via API:', { planType, paymentToken });
          
          // Fixed: Use the renamed upgradeSubscription method instead of createSubscription
          const response = await apiService.upgradeSubscription(planType, paymentToken);
          
          if (response.success) {
            console.log('✅ Subscription upgrade successful, refreshing user data...');
            // Refresh user data to get updated subscription
            await get().refreshUser();
            set({ isLoading: false });
            return true;
          }
          
          console.error('❌ Subscription upgrade failed:', response.message);
          set({ isLoading: false });
          return false;
        } catch (error) {
          console.error('❌ Activate subscription error:', error);
          set({ isLoading: false });
          return false;
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        userStatus: state.userStatus
      })
    }
  )
); 