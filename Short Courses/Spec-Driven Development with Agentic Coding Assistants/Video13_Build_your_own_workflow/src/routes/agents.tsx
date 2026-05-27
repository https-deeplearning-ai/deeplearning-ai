import { Hono } from "hono";
import type Database from "better-sqlite3";
import { AgentsList } from "../components/AgentsList";
import { AgentDetail } from "../components/AgentDetail";
import type { Agent, Ailment } from "../db/types";

export function agentsRouter(db: Database.Database) {
  const router = new Hono();

  const selectAll = db.prepare("SELECT * FROM agents ORDER BY name");
  const selectById = db.prepare("SELECT * FROM agents WHERE id = ?");
  const selectAilments = db.prepare(
    `SELECT al.* FROM ailments al
     JOIN agent_ailments aa ON al.id = aa.ailment_id
     WHERE aa.agent_id = ?
     ORDER BY al.name`
  );

  router.get("/", (c) => {
    const agents = selectAll.all() as Agent[];
    return c.html(<AgentsList agents={agents} />);
  });

  router.get("/:id", (c) => {
    const id = Number(c.req.param("id"));
    const agent = selectById.get(id) as Agent | undefined;
    if (!agent) return c.notFound();
    const ailments = selectAilments.all(id) as Ailment[];
    return c.html(<AgentDetail agent={agent} ailments={ailments} />);
  });

  return router;
}
