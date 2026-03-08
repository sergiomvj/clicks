import { NextResponse } from "next/server";

import { getSession } from "@/lib/session";

export async function POST(request: Request) {
  const formData = await request.formData();
  const email = String(formData.get("email") || "").trim().toLowerCase();
  const password = String(formData.get("password") || "");

  const expectedEmail = (process.env.DASHBOARD_EMAIL || "owner@facebrasil.test").toLowerCase();
  const expectedPassword = process.env.DASHBOARD_PASSWORD || "change-me";

  if (email !== expectedEmail || password !== expectedPassword) {
    return NextResponse.redirect(new URL("/login", request.url), { status: 303 });
  }

  const session = await getSession();
  session.isLoggedIn = true;
  session.email = email;
  session.userId = process.env.DASHBOARD_USER_ID || "owner-facebrasil";
  session.workspaceId =
    process.env.DASHBOARD_WORKSPACE_ID || "10000000-0000-0000-0000-000000000001";
  session.agentId = "dashboard-ui";
  await session.save();

  return NextResponse.redirect(new URL("/dashboard", request.url), { status: 303 });
}
