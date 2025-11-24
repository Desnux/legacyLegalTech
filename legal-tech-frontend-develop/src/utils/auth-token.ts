import { serialize } from "cookie";
import Cookies from "js-cookie";

export const AUTH_COOKIE = "auth-token";
export const USER_GROUP = "user-group";
export const LOGIN_ROUTE = "/login";
export const DEFAULT_ROUTE = "/";
export const RECEPTHOR_AUTH_COOKIE = "recepthor-auth-token";

export function setAuthToken(res: Response, token: string) {
  res.headers.append(
    "Set-Cookie",
    serialize(AUTH_COOKIE, token, {
      httpOnly: true,
      path: "/",
      maxAge: 60 * 60 * 24,
    })
  );
}

export function removeAuthToken(res: Response) {
  res.headers.append(
    "Set-Cookie",
    serialize(AUTH_COOKIE, "", {
      httpOnly: true,
      path: "/",
      maxAge: 0,
    })
  );
}

export function setAuthTokenClient(token: string) {
  Cookies.set(AUTH_COOKIE, token, { expires: 1, path: "/" });
}

export function setRecepthorAuthTokenClient(token: string) {
  Cookies.set(RECEPTHOR_AUTH_COOKIE, token, { expires: 1, path: "/" });
}

export function getAuthTokenClient(): string | undefined {
  const token = Cookies.get(AUTH_COOKIE);
  return token;
}

export function getRecepthorAuthTokenClient(): string | undefined {
  const token = Cookies.get(RECEPTHOR_AUTH_COOKIE);
  return token;
}

export function removeAuthTokenClient() {
  Cookies.remove(AUTH_COOKIE, { path: "/" });
}

export function removeRecepthorAuthTokenClient() {
  Cookies.remove(RECEPTHOR_AUTH_COOKIE, { path: "/" });
}

export function removeUserGroup(res: Response) {
  res.headers.append(
    "Set-Cookie",
    serialize(USER_GROUP, "", {
      httpOnly: true,
      path: "/",
      maxAge: 0,
    })
  );
}

export function setUserGroupClient(group: string | null) {
  Cookies.set(USER_GROUP, group ?? "", { expires: 1, path: "/" });
}

export function getUserGroupClient(): string | undefined {
  const group = Cookies.get(USER_GROUP);
  return group;
}

export function removeUserGroupClient() {
  Cookies.remove(USER_GROUP, { path: "/" });
}
