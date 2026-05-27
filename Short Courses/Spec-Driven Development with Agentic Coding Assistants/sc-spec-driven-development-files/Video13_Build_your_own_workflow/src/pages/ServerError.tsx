import { FC } from "hono/jsx";
import { Layout } from "../components/Layout";

export const ServerError: FC = () => (
  <Layout>
    <article>
      <header>
        <h1>Something Went Wrong</h1>
      </header>
      <p>An unexpected error occurred. Please try again later.</p>
      <a href="/">← Return home</a>
    </article>
  </Layout>
);
