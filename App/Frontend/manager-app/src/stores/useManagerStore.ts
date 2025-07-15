import { create } from 'zustand';

interface Manager {
  id: number;
  name: string;
  email: string;
  department: string;
}

interface ManagerStore {
  manager: Manager | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (phone: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshProfile: () => Promise<Manager | null>;
}

// API base URL
const API_BASE_URL = process.env.NODE_ENV === 'production' ? 'https://api.rent-assistant.ru' : 'http://localhost:8000';

export const useManagerStore = create<ManagerStore>((set, get) => ({
      manager: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      login: async (phone: string, password: string): Promise<boolean> => {
    console.log('🔐 Starting manager login process...');
    console.log('📞 Phone:', phone);
    console.log('🌐 API URL:', `${API_BASE_URL}/api/v1/management/auth/login`);
    
        set({ loading: true });
        try {
      const requestBody = JSON.stringify({ phone, password });
      console.log('📤 Request body:', requestBody);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/management/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
        body: requestBody,
          });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response ok:', response.ok);

          if (response.ok) {
            const data = await response.json();
        console.log('✅ Login successful, received data:', data);
        
            const token = data.access_token;
            
        // Сохраняем токен в localStorage перед обновлением профиля
            localStorage.setItem('manager_token', token);
        set({ token }); // Устанавливаем токен в состояние
            
        // Обновляем профиль и получаем данные менеджера
        console.log('🔄 Fetching manager profile...');
        const manager = await get().refreshProfile();
        console.log('👤 Manager profile:', manager);
        
        set({ manager, isAuthenticated: true, loading: false });
            return true;
          } else {
        const errorText = await response.text();
        console.error('❌ Login failed. Response:', errorText);
            set({ loading: false });
            return false;
          }
        } catch (error) {
      console.error('❌ Login error:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
          set({ loading: false });
          return false;
        }
      },

      logout: () => {
        localStorage.removeItem('manager_token');
        set({ 
          manager: null, 
          token: null, 
          isAuthenticated: false 
        });
      },

  refreshProfile: async (): Promise<Manager | null> => {
        const token = get().token || localStorage.getItem('manager_token');
    console.log('🔄 RefreshProfile called, token exists:', !!token);
    
    if (!token) return null;

        try {
      console.log('📤 Fetching profile from:', `${API_BASE_URL}/api/v1/management/profile`);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/management/profile`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

      console.log('📥 Profile response status:', response.status);

          if (response.ok) {
            const manager = await response.json();
        console.log('✅ Profile fetched successfully:', manager);
            set({ manager, isAuthenticated: true, token });
        return manager;
          } else {
            // Token invalid
        console.error('❌ Profile fetch failed, logging out');
            get().logout();
        return null;
          }
        } catch (error) {
      console.error('❌ Profile refresh error:', error);
          get().logout();
      return null;
        }
      },
}));

// Initialize from localStorage on app load
const token = localStorage.getItem('manager_token');
if (token) {
  console.log('🔑 Found token in localStorage, refreshing profile...');
  useManagerStore.getState().refreshProfile();
} 