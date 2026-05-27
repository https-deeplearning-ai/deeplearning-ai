import { FC } from "hono/jsx";
import { Layout } from "./Layout";

type FormErrors = {
  therapist_name?: string;
  date?: string;
  time?: string;
  general?: string;
};

type FormValues = {
  therapist_name?: string;
  date?: string;
  time?: string;
};

type AppointmentFormProps = {
  agentId: number;
  agentName: string;
  errors?: FormErrors;
  values?: FormValues;
};

export const AppointmentForm: FC<AppointmentFormProps> = ({
  agentId,
  agentName,
  errors = {},
  values = {},
}) => (
  <Layout>
    <h1>Book an Appointment</h1>
    <p>
      Agent: <strong>{agentName}</strong>
    </p>
    <form method="post" action={`/agents/${agentId}/appointments`}>
      <label>
        Therapist Name
        <input
          type="text"
          name="therapist_name"
          value={values.therapist_name ?? ""}
          required
          aria-describedby={errors.therapist_name ? "err-therapist" : undefined}
        />
        {errors.therapist_name && (
          <small id="err-therapist">{errors.therapist_name}</small>
        )}
      </label>
      <label>
        Date
        <input
          type="date"
          name="date"
          value={values.date ?? ""}
          required
          aria-describedby={errors.date ? "err-date" : undefined}
        />
        {errors.date && <small id="err-date">{errors.date}</small>}
      </label>
      <label>
        Time
        <input
          type="time"
          name="time"
          value={values.time ?? ""}
          required
          aria-describedby={errors.time ? "err-time" : undefined}
        />
        {errors.time && <small id="err-time">{errors.time}</small>}
      </label>
      {errors.general && (
        <p>
          <strong>{errors.general}</strong>
        </p>
      )}
      <button type="submit">Book Appointment</button>
    </form>
    <p>
      <a href={`/agents/${agentId}`}>← Back to agent</a>
    </p>
  </Layout>
);
