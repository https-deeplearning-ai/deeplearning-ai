import { FC } from "hono/jsx";
import { Layout } from "./Layout";
import type { Appointment } from "../db/types";

type AppointmentConfirmationProps = {
  appointment: Appointment;
  agentName: string;
};

export const AppointmentConfirmation: FC<AppointmentConfirmationProps> = ({
  appointment,
  agentName,
}) => (
  <Layout>
    <article>
      <header>
        <h1>Appointment Confirmed</h1>
      </header>
      <p>
        <strong>Agent:</strong> {agentName}
      </p>
      <p>
        <strong>Therapist:</strong> {appointment.therapist_name}
      </p>
      <p>
        <strong>Scheduled:</strong> {appointment.scheduled_at}
      </p>
      <p>
        <strong>Status:</strong> {appointment.status}
      </p>
    </article>
    <p>
      <a href={`/agents/${appointment.agent_id}`}>← Back to agent</a>
    </p>
  </Layout>
);
