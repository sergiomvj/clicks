export async function apiFetch(path: string, init?: RequestInit) {
  const response = await fetch(`/api/proxy/${path.replace(/^\/+/, "")}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Proxy request failed with status ${response.status}`);
  }

  return response;
}
