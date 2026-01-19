import React, { createContext, useContext, useState, useEffect } from 'react';
import { getUser, clearAuthData, setAuthData, isAuthenticated } from '../lib/auth-utils';

interface AuthContextType {
    user: any | null;
    isLoading: boolean;
    isAuth: boolean;
    login: (accessToken: string, refreshToken?: string, user?: any) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<any | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isAuth, setIsAuth] = useState(false);

    useEffect(() => {
        const loadAuthData = async () => {
            const authenticated = await isAuthenticated();
            if (authenticated) {
                const userData = await getUser();
                setUser(userData);
                setIsAuth(true);
            }
            setIsLoading(false);
        };

        loadAuthData();
    }, []);

    const login = async (accessToken: string, refreshToken?: string, userData?: any) => {
        await setAuthData(accessToken, refreshToken, userData);
        setUser(userData);
        setIsAuth(true);
    };

    const logout = async () => {
        await clearAuthData();
        setUser(null);
        setIsAuth(false);
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, isAuth, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
