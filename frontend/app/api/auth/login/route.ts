import { NextResponse } from "next/server";

import { getSession } from "@/lib/session";

export async function POST(request: Request) {
  const formData = await request.formData();
  const email = String(formData.get("email") || "").trim();
  const password = String(formData.get("password") || "").trim();

  if (email !== process.env.DASHBOARD_EMAIL || password !== process.env.DASHBOARD_PASSWORD) {
    return NextResponse.redirect(new URL("/login", request.url), { status: 303 });
  }

  const session = await getSession();
  session.isLoggedIn = true;
  session.email = email;
  session.userId = process.env.DASHBOARD_USER_ID;
  session.workspaceId = process.env.DASHBOARD_WORKSPACE_ID;
  await session.save();

  return NextResponse.redirect(new URL("/spaces", request.url), { status: 303 });
}
