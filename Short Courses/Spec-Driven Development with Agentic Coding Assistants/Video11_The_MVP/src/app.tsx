import { Hono } from "hono";
import { serveStatic } from "@hono/node-server/serve-static";
import type Database from "better-sqlite3";
import { Home } from "./pages/Home";
import { agentsRouter } from "./routes/agents";
import { ailmentsRouter } from "./routes/ailments";

export function createApp(db: Database.Database) {
  const app = new Hono();

  app.use("/static/*", serveStatic({ root: "./" }));

  app.get("/", (c) => c.html(<Home />));
  app.route("/agents", agentsRouter(db));
  app.route("/ailments", ailmentsRouter(db));

  return app;
}
