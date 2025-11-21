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
}

export const AuthContext = createContext<AuthContextType>({ 
  token: null,
  group: null,
  setAuth: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>({ token: null, group: null });

  useEffect(() => {
    const t = Cookies.get(AUTH_COOKIE) || null
    const g = Cookies.get(USER_GROUP) || null
    setAuth({ token: t, group: g })
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, setAuth }}>
      {children}
    </AuthContext.Provider>
  );
}
