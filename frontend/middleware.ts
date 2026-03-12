import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPrefixes = ["/spaces"];

export function middleware(request: NextRequest) {
  const isProtected = protectedPrefixes.some((prefix) => request.nextUrl.pathname.startsWith(prefix));
  const sessionCookie = request.cookies.get("fbr_clicks_session");

  if (isProtected && !sessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (request.nextUrl.pathname === "/login" && sessionCookie) {
    return NextResponse.redirect(new URL("/spaces", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/spaces/:path*", "/login"],
};
