export const LOGIN_ROUTE = "/ingresar";
export const DEFAULT_ROUTE = "/demand-text/generator";

export const setAuthToken = (token: string, expiresInMinutes: number) => {
  const expiresAt = Date.now() + expiresInMinutes * 60 * 1000;
  const tokenData = { token, expiresAt };
  
  sessionStorage.setItem("auth-token", JSON.stringify(tokenData));
};

export const getAuthToken = (): string | null => {
  const tokenData = sessionStorage.getItem("auth-token");

  if (!tokenData) return null;
  
  const { token, expiresAt } = JSON.parse(tokenData);
  
  if (Date.now() > expiresAt) {
    sessionStorage.removeItem("auth-token");
    return null;
  }
  
  return token;
};

export const removeAuthToken = () => {
  sessionStorage.removeItem("auth-token");
};

export const setPreviousRoute = (route: string) => {
  sessionStorage.setItem("previous-route", route);
};

export const getPreviousRoute = () => {
  const route = sessionStorage.getItem("previous-route");
  
  if (!route) {
    return DEFAULT_ROUTE;
  }

  return route;
};

export const removePreviousRoute = () => {
  sessionStorage.removeItem("previous-route");
};


