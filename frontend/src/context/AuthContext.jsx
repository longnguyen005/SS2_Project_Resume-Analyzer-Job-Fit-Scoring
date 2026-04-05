import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { AUTH_CHANGED_EVENT, clearToken, getToken, saveToken } from "../lib/auth";
import { apiRequest } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(false);

  const login = useCallback((nextToken) => {
    saveToken(nextToken);
    setToken(nextToken);
  }, []);

  const logout = useCallback(() => {
    clearToken();
    setToken(null);
    setCurrentUser(null);
  }, []);

  useEffect(() => {
    function syncAuthState() {
      setToken(getToken());
    }

    window.addEventListener("storage", syncAuthState);
    window.addEventListener(AUTH_CHANGED_EVENT, syncAuthState);
    return () => {
      window.removeEventListener("storage", syncAuthState);
      window.removeEventListener(AUTH_CHANGED_EVENT, syncAuthState);
    };
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    if (!getToken()) {
      setCurrentUser(null);
      return null;
    }

    setIsLoadingUser(true);

    try {
      const user = await apiRequest("/auth/me");
      setCurrentUser(user);
      return user;
    } catch (error) {
      setCurrentUser(null);
      return null;
    } finally {
      setIsLoadingUser(false);
    }
  }, []);

  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      setIsLoadingUser(false);
      return;
    }

    refreshCurrentUser();
  }, [refreshCurrentUser, token]);

  const value = useMemo(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      currentUser,
      isLoadingUser,
      login,
      logout,
      refreshCurrentUser,
    }),
    [currentUser, isLoadingUser, login, logout, refreshCurrentUser, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
