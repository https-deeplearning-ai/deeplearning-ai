import { FC } from "hono/jsx";
import { Layout } from "../components/Layout";
import { FeedbackForm } from "../components/FeedbackForm";
import { FeedbackList } from "../components/FeedbackList";
import type { Feedback } from "../db/types";

type Props = {
  items: Feedback[];
  errors?: Record<string, string>;
  values?: { name: string; email: string; message: string; rating: string };
};

export const FeedbackPage: FC<Props> = ({ items, errors, values }) => (
  <Layout>
    <h1>Feedback</h1>
    <p>Share your experience with the clinic. All agents and curious humans welcome.</p>
    <FeedbackForm errors={errors} values={values} />
    <h2>What Others Have Said</h2>
    <FeedbackList items={items} />
  </Layout>
);
