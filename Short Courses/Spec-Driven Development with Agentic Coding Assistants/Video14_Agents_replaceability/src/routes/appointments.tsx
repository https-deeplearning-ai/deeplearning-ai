import { Hono } from "hono";
import type Database from "better-sqlite3";
import { AppointmentForm } from "../components/AppointmentForm";
import { AppointmentConfirmation } from "../components/AppointmentConfirmation";
import type { Agent, Appointment } from "../db/types";

function stripHtml(input: string): string {
  return input.replace(/<[^>]*>/g, "").trim();
}

export function appointmentsRouter(db: Database.Database) {
  const router = new Hono();

  const selectAgent = db.prepare("SELECT * FROM agents WHERE id = ?");
  const insertAppointment = db.prepare(
    "INSERT INTO appointments (agent_id, therapist_name, scheduled_at) VALUES (?, ?, ?)"
  );
  const selectAppointment = db.prepare(
    "SELECT * FROM appointments WHERE id = ?"
  );

  router.get("/:id/appointments/new", (c) => {
    const id = Number(c.req.param("id"));
    const agent = selectAgent.get(id) as Agent | undefined;
    if (!agent) return c.notFound();
    return c.html(<AppointmentForm agentId={id} agentName={agent.name} />);
  });

  router.post("/:id/appointments", async (c) => {
    const id = Number(c.req.param("id"));
    const agent = selectAgent.get(id) as Agent | undefined;
    if (!agent) return c.notFound();

    const body = await c.req.parseBody();
    const therapist_name = stripHtml(String(body.therapist_name ?? ""));
    const date = String(body.date ?? "").trim();
    const time = String(body.time ?? "").trim();

    const errors: Record<string, string> = {};
    if (!therapist_name) errors.therapist_name = "Therapist name is required.";
    if (!date) errors.date = "Date is required.";
    if (!time) errors.time = "Time is required.";

    if (Object.keys(errors).length === 0) {
      const scheduled_at = `${date}T${time}:00`;
      if (new Date(scheduled_at) <= new Date()) {
        errors.general = "Appointment must be scheduled in the future.";
      }
    }

    if (Object.keys(errors).length > 0) {
      return c.html(
        <AppointmentForm
          agentId={id}
          agentName={agent.name}
          errors={errors}
          values={{ therapist_name, date, time }}
        />
      );
    }

    const scheduled_at = `${date}T${time}:00`;
    const result = insertAppointment.run(id, therapist_name, scheduled_at);
    const apptId = Number(result.lastInsertRowid);
    return c.redirect(`/agents/${id}/appointments/${apptId}`);
  });

  router.get("/:id/appointments/:apptId", (c) => {
    const id = Number(c.req.param("id"));
    const apptId = Number(c.req.param("apptId"));
    const agent = selectAgent.get(id) as Agent | undefined;
    if (!agent) return c.notFound();
    const appointment = selectAppointment.get(apptId) as Appointment | undefined;
    if (!appointment) return c.notFound();
    return c.html(
      <AppointmentConfirmation appointment={appointment} agentName={agent.name} />
    );
  });

  return router;
}
