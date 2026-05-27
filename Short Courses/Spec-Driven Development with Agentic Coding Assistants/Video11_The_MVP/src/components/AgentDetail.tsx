import { FC } from "hono/jsx";
import { Layout } from "./Layout";
import type { Agent, Ailment } from "../db/types";

type AgentDetailProps = { agent: Agent; ailments: Ailment[] };

export const AgentDetail: FC<AgentDetailProps> = ({
  agent,
  ailments,
}) => (
  <Layout>
    <article>
      <header>
        <h1>{agent.name}</h1>
      </header>
      <p>
        <strong>Model:</strong> {agent.model_type}
      </p>
      <p>
        <strong>Status:</strong> {agent.status.replace("_", " ")}
      </p>
      {ailments.length > 0 && (
        <>
          <h2>Presenting Complaints</h2>
          <ul>
            {ailments.map((a) => (
              <li key={a.id}>
                <strong>{a.name}</strong> — {a.description}
              </li>
            ))}
          </ul>
        </>
      )}
    </article>
    <p>
      <a href="/agents">← Back to agents</a>
    </p>
  </Layout>
);
