const test = require("node:test");
const assert = require("node:assert/strict");
const { createApp } = require("./server");

test("GET /health returns ok", async () => {
  const app = createApp();
  const server = app.listen(0);
  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/health`);
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.status, "ok");
  await new Promise((resolve) => server.close(resolve));
});
