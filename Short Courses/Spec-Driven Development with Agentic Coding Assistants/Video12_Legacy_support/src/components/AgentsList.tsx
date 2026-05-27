import { FC } from "hono/jsx";
import { Layout } from "./Layout";
import type { Agent } from "../db/types";

type AgentsListProps = { agents: Agent[] };

export const AgentsList: FC<AgentsListProps> = ({ agents }) => (
  <Layout>
    <h1>Agents</h1>
    <table>
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Model</th>
          <th scope="col">Status</th>
        </tr>
      </thead>
      <tbody>
        {agents.map((a) => (
          <tr key={a.id}>
            <td>
              <a href={`/agents/${a.id}`}>{a.name}</a>
            </td>
            <td>{a.model_type}</td>
            <td>{a.status.replace("_", " ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </Layout>
);
