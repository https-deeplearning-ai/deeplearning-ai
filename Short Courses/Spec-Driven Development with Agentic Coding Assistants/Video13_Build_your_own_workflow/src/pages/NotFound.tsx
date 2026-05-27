import { FC } from "hono/jsx";
import { Layout } from "../components/Layout";

export const NotFound: FC = () => (
  <Layout>
    <article>
      <header>
        <h1>Page Not Found</h1>
      </header>
      <p>The page you&apos;re looking for doesn&apos;t exist.</p>
      <a href="/">← Return home</a>
    </article>
  </Layout>
);
