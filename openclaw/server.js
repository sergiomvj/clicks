const http = require('http');

const port = Number(process.env.OPENCLAW_PORT || 3500);

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, { 'Content-Type': 'application/json' });
  response.end(JSON.stringify(payload));
}

const server = http.createServer((request, response) => {
  if (request.method === 'GET' && request.url === '/health') {
    sendJson(response, 200, {
      status: 'ok',
      gateway: 'openclaw-scaffold',
      workspace_id: process.env.OPENCLAW_WORKSPACE_ID || null,
    });
    return;
  }

  if (request.method === 'POST' && request.url === '/agents/register') {
    let body = '';
    request.on('data', (chunk) => {
      body += chunk.toString();
    });
    request.on('end', () => {
      sendJson(response, 202, {
        status: 'accepted',
        message: 'Gateway scaffold received registration payload.',
        payload_size: body.length,
      });
    });
    return;
  }

  sendJson(response, 404, { detail: 'Not found.' });
});

server.listen(port, '0.0.0.0');
