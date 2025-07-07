import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Assistant {
  id: number;
  name: string;
  email: string;
  telegram_username?: string;
  specialization: string;
  status: string;
  current_active_tasks: number;
  total_tasks_completed: number;
  average_rating: number;
}

interface AssistantStore {
  assistant: Assistant | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (phone: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
  updateStatus: (status: 'online' | 'offline') => Promise<boolean>;
}

// API base URL
const API_BASE_URL = 'https://api.rent-assistant.ru';

export const useAssistantStore = create<AssistantStore>()(
  persist(
    (set, get) => ({
      assistant: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      login: async (phone: string, password: string): Promise<boolean> => {
        set({ loading: true });
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/assistants/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ phone, password }),
          });

          if (response.ok) {
            const data = await response.json();
            const token = data.access_token;
            
            set({ token, isAuthenticated: true });
            localStorage.setItem('assistant_token', token);
            
            // Get profile
            await get().refreshProfile();
            set({ loading: false });
            return true;
          } else {
            set({ loading: false });
            return false;
          }
        } catch (error) {
          console.error('Login error:', error);
          set({ loading: false });
          return false;
        }
      },

      logout: () => {
        localStorage.removeItem('assistant_token');
        set({ 
          assistant: null, 
          token: null, 
          isAuthenticated: false 
        });
      },

      refreshProfile: async () => {
        const token = get().token || localStorage.getItem('assistant_token');
        if (!token) return;

        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/assistants/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const assistant = await response.json();
            set({ assistant, isAuthenticated: true, token });
          } else {
            // Token invalid
            get().logout();
          }
        } catch (error) {
          console.error('Profile refresh error:', error);
          get().logout();
        }
      },

      updateStatus: async (status: 'online' | 'offline'): Promise<boolean> => {
        const token = get().token;
        if (!token) return false;

        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/assistants/profile/status`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status }),
          });

          if (response.ok) {
            // Update local state
            const assistant = get().assistant;
            if (assistant) {
              set({ 
                assistant: { ...assistant, status } 
              });
            }
            return true;
          }
          return false;
        } catch (error) {
          console.error('Status update error:', error);
          return false;
        }
      },
    }),
    {
      name: 'assistant-storage',
      partialize: (state) => ({
        token: state.token,
        assistant: state.assistant,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 