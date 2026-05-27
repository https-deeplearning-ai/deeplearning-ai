import { FC } from "hono/jsx";
import { Layout } from "./Layout";
import type { Ailment } from "../db/types";

type AilmentsListProps = { ailments: Ailment[] };

export const AilmentsList: FC<AilmentsListProps> = ({ ailments }) => (
  <Layout>
    <h1>Ailments</h1>
    <table>
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Description</th>
        </tr>
      </thead>
      <tbody>
        {ailments.map((a) => (
          <tr key={a.id}>
            <td>{a.name}</td>
            <td>{a.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </Layout>
);
