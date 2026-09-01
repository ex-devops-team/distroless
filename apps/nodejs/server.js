const http = require("http");
const express = require("express");

function createApp() {
  const app = express();
  app.get("/health", (_req, res) => {
    res.status(200).json({ status: "ok", language: "nodejs", stack: "express" });
  });
  return app;
}

if (require.main === module) {
  const port = Number(process.env.PORT || 8080);
  createApp().listen(port, "0.0.0.0", () => {
    console.log(`listening on :${port}`);
  });
}

module.exports = { createApp, http };
