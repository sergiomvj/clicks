import { NextResponse } from "next/server";

import { getSession } from "@/lib/session";

const methods = ["GET", "POST", "PATCH", "DELETE"] as const;

async function proxyRequest(request: Request, path: string[]) {
  const session = await getSession();
  if (!session.isLoggedIn || !session.workspaceId) {
    return new NextResponse(null, { status: 401 });
  }

  const incomingUrl = new URL(request.url);
  const search = incomingUrl.search;
  const upstream = `${process.env.BACKEND_URL || "http://localhost:8000"}/api/${path.join("/")}${search}`;
  const body = request.method === "GET" || request.method === "DELETE" ? undefined : await request.text();

  const response = await fetch(upstream, {
    method: request.method,
    headers: {
      "Content-Type": request.headers.get("content-type") || "application/json",
      "X-Workspace-Id": session.workspaceId,
      "X-Agent-Id": session.agentId || "dashboard-ui",
    },
    body,
    cache: "no-store",
  });

  return new NextResponse(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") || "application/json",
    },
  });
}

export async function GET(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  return proxyRequest(request, params.path);
}

export async function POST(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  return proxyRequest(request, params.path);
}

export async function PATCH(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  return proxyRequest(request, params.path);
}

export async function DELETE(
  request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const params = await context.params;
  return proxyRequest(request, params.path);
}
