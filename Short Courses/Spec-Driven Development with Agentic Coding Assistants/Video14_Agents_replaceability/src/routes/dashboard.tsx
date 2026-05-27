import { Hono } from "hono";
import type Database from "better-sqlite3";
import { Dashboard } from "../components/Dashboard";

export function dashboardRouter(db: Database.Database) {
  const router = new Hono();

  const countAgents = db.prepare("SELECT COUNT(*) as count FROM agents");
  const countOpenAppointments = db.prepare(
    "SELECT COUNT(*) as count FROM appointments WHERE status IN ('pending', 'confirmed')"
  );
  const countActiveAilments = db.prepare(
    `SELECT COUNT(DISTINCT aa.ailment_id) as count
     FROM agent_ailments aa
     JOIN agents a ON aa.agent_id = a.id
     WHERE a.status = 'active'`
  );
  const selectAgents = db.prepare(
    "SELECT id, name, model_type, status FROM agents ORDER BY name"
  );
  const selectUpcomingAppointments = db.prepare(
    `SELECT ap.id, a.name as agent_name, ap.therapist_name, ap.scheduled_at, ap.status
     FROM appointments ap
     JOIN agents a ON ap.agent_id = a.id
     WHERE ap.status IN ('pending', 'confirmed')
     ORDER BY ap.scheduled_at`
  );
  const selectAilments = db.prepare(
    `SELECT al.id, al.name, COUNT(aa.agent_id) as agent_count
     FROM ailments al
     LEFT JOIN agent_ailments aa ON al.id = aa.ailment_id
     GROUP BY al.id, al.name
     ORDER BY al.name`
  );

  router.get("/", (c) => {
    const stats = {
      agentCount: (countAgents.get() as { count: number }).count,
      openAppointmentCount: (countOpenAppointments.get() as { count: number })
        .count,
      activeAilmentCount: (countActiveAilments.get() as { count: number })
        .count,
    };
    const agents = selectAgents.all() as {
      id: number;
      name: string;
      model_type: string;
      status: string;
    }[];
    const appointments = selectUpcomingAppointments.all() as {
      id: number;
      agent_name: string;
      therapist_name: string;
      scheduled_at: string;
      status: string;
    }[];
    const ailments = selectAilments.all() as {
      id: number;
      name: string;
      agent_count: number;
    }[];

    return c.html(
      <Dashboard
        stats={stats}
        agents={agents}
        appointments={appointments}
        ailments={ailments}
      />
    );
  });

  return router;
}
