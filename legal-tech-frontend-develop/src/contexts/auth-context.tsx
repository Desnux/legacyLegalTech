"use client";

import { createContext, useState, useEffect, ReactNode } from "react";
import Cookies from "js-cookie";
import { AUTH_COOKIE, USER_GROUP } from "@/utils/auth-token";

export interface AuthState {
  token: string | null;
  group: string | null;
}

interface AuthContextType extends AuthState {
  setAuth: (auth: AuthState) => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType>({ 
  token: null,
  group: null,
  setAuth: () => {},
  isLoading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({ token: null, group: null });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const t = Cookies.get(AUTH_COOKIE) || null
    const g = Cookies.get(USER_GROUP) || null
    setAuth({ token: t, group: g })
    setIsLoading(false);
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, setAuth, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}
