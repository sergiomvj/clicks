import { cookies } from "next/headers";
import { getIronSession, type SessionOptions } from "iron-session";

export interface SessionData {
  isLoggedIn: boolean;
  workspaceId?: string;
  userId?: string;
  email?: string;
}

const fallbackSecret = "replace-with-64-char-secret-replace-with-64-char-secret-1234";

export const sessionOptions: SessionOptions = {
  password: process.env.SESSION_SECRET || fallbackSecret,
  cookieName: "fbr_clicks_session",
  cookieOptions: {
    httpOnly: true,
    secure: process.env.APP_ENV === "production",
    sameSite: "lax",
    path: "/",
  },
};

export async function getSession() {
  return getIronSession<SessionData>(await cookies(), sessionOptions);
}
