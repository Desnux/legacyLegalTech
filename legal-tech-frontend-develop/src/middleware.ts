import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { AUTH_COOKIE, DEFAULT_ROUTE, LOGIN_ROUTE, USER_GROUP } from "@/utils/auth-token";

export function middleware(req: NextRequest) {
  const { pathname, origin } = req.nextUrl;
  const token = req.cookies.get(AUTH_COOKIE)?.value;
  const group = req.cookies.get(USER_GROUP)?.value;

  if (pathname.startsWith("/_next") || pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  if (pathname === "/test") {
    return NextResponse.next();
  }

  if (pathname === LOGIN_ROUTE && token) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (pathname !== LOGIN_ROUTE && !token) {
    const loginUrl = new URL(LOGIN_ROUTE, origin);
    loginUrl.searchParams.set("callbackUrl", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (group === "admin") {
    return NextResponse.next();
  }

  if (group !== "admin" && group !== "lawyer" && pathname.startsWith("/demand-text")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (group !== "lawyer" && group !== "supervisor" && group !== "admin" && pathname.startsWith("/supervisor")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (group !== "lawyer" && group !== "admin" && pathname.startsWith("/preliminary-measure")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (group !== "admin" && pathname.startsWith("/users")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (group !== "admin" && group !== "supervisor" && group !== "lawyer" && pathname.startsWith("/case/")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  return NextResponse.next();
}

export const config = {
  matcher: "/:path*",
};
