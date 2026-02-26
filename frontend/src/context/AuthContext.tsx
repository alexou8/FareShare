/**
 * Authentication Context
 * Manages global authentication state, user data, and auth operations
 * Provides login, register, logout functionality to the entire app
 */

import { createContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthContextType, User, RegisterData, TokenResponse } from '../types';
import { apiGet, apiPost, setAuthToken, getAuthToken, removeAuthToken } from '../utils/api';

/**
 * Create the authentication context
 * This will be used by the useAuth hook to access auth state
 */
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider Props
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication Provider Component
 * Wraps the app to provide authentication state and methods to all components
 * 
 * Usage:
 * ```tsx
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 * ```
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Initialize authentication state on app load
   * Checks localStorage for existing token and validates it
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if token exists in localStorage
        const storedToken = getAuthToken();
        
        if (storedToken) {
          // Token exists - validate it by fetching user profile
          setToken(storedToken);
          await fetchUserProfile();
        }
      } catch (error) {
        // Token is invalid or expired - clear it
        console.error('Failed to initialize auth:', error);
        removeAuthToken();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Fetch current user's profile from the backend
   * Called after login or on app initialization to get user data
   */
  const fetchUserProfile = async () => {
    try {
      const userData = await apiGet<User>('/api/users/me');
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      throw error;
    }
  };

  /**
   * Register a new user account
   * Creates account and automatically logs in the user
   * 
   * @param data - Registration data (full_name, email, password)
   * @throws ApiClientError if registration fails
   */
  const register = async (data: RegisterData) => {
    try {
      // Call registration endpoint
      await apiPost<User>('/api/auth/register', data);
      
      // Registration successful - now login automatically
      await login(data.email, data.password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  /**
   * Login user with email and password
   * Stores JWT token and fetches user profile on success
   * 
   * @param email - User's email address
   * @param password - User's password
   * @throws ApiClientError if login fails
   */
  const login = async (email: string, password: string) => {
    try {
      // Call login endpoint
      const response = await apiPost<TokenResponse>('/api/auth/login', {
        email,
        password,
      });
      
      // Store token in state and localStorage
      const accessToken = response.access_token;
      setToken(accessToken);
      setAuthToken(accessToken);
      
      // Fetch full user profile
      await fetchUserProfile();
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  /**
   * Logout user
   * Clears token from localStorage and resets auth state
   */
  const logout = () => {
    // Clear token from localStorage
    removeAuthToken();
    
    // Reset state
    setToken(null);
    setUser(null);
    
    // Optionally call backend logout endpoint
    // apiPost('/api/auth/logout').catch(() => {});
  };

  /**
   * Context value provided to consuming components
   */
  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    setUser, // Expose setUser so components can update user data
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
