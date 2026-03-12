import { NextResponse } from "next/server";

import { getSession } from "@/lib/session";

async function forward(request: Request, path: string[]) {
  const session = await getSession();
  if (!session.isLoggedIn || !session.userId || !session.workspaceId) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }

  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    return NextResponse.json({ detail: "BACKEND_URL missing" }, { status: 500 });
  }

  const target = `${backendUrl}/api/${path.join("/")}`;
  const headers = new Headers(request.headers);
  headers.set("X-User-Id", session.userId);
  headers.set("X-Workspace-Id", session.workspaceId);
  headers.delete("host");

  const response = await fetch(target, {
    method: request.method,
    headers,
    body: request.method === "GET" ? undefined : await request.text(),
    cache: "no-store",
  });

  const text = await response.text();
  return new NextResponse(text, {
    status: response.status,
    headers: { "content-type": response.headers.get("content-type") || "application/json" },
  });
}

export const GET = async (request: Request, context: { params: Promise<{ path: string[] }> }) => {
  const { path } = await context.params;
  return forward(request, path);
};
export const POST = GET;
export const PATCH = GET;
export const PUT = GET;
export const DELETE = GET;
