import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { AUTH_COOKIE, DEFAULT_ROUTE, LOGIN_ROUTE, USER_GROUP } from "@/utils/auth-token";

export function middleware(req: NextRequest) {
  const { pathname, origin } = req.nextUrl;
  const token = req.cookies.get(AUTH_COOKIE)?.value;

  if (pathname.startsWith("/_next") || pathname.startsWith("/api")) {
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

  const group = req.cookies.get(USER_GROUP)?.value;

  if (group !== "executive_case" && (pathname.startsWith("/demand-text") || pathname.startsWith("/supervisor"))) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  if (group !== "in_house_suite" && pathname.startsWith("/preliminary-measure")) {
    return NextResponse.redirect(new URL(DEFAULT_ROUTE, origin));
  }

  return NextResponse.next();
}

export const config = {
  matcher: "/:path*",
};
