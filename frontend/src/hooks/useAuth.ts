/**
 * useAuth Hook
 * Custom hook to access authentication context throughout the app
 * 
 * Usage:
 * ```tsx
 * const { user, isAuthenticated, login, logout } = useAuth();
 * ```
 */

import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import type { AuthContextType } from '../types';

/**
 * Access authentication state and methods
 * Must be used within an AuthProvider
 * 
 * @returns Authentication context with user, token, and auth methods
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
    const context = useContext(AuthContext);

    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }

    return context;
}
