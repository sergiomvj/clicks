const http = require("http");
const port = Number(process.env.OPENCLAW_PORT || 3500);
const workspaceId = process.env.OPENCLAW_WORKSPACE_ID || "unknown";

const server = http.createServer((request, response) => {
  if (request.url === "/health") {
    response.writeHead(200, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ status: "ok", workspaceId }));
    return;
  }

  response.writeHead(404, { "Content-Type": "application/json" });
  response.end(JSON.stringify({ detail: "Not found" }));
});

server.listen(port, () => {
  console.log(`OpenClaw scaffold listening on ${port}`);
});
