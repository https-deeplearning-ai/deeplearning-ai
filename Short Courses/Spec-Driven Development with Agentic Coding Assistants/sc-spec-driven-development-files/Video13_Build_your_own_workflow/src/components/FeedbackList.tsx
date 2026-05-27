import { FC } from "hono/jsx";
import type { Feedback } from "../db/types";

type Props = { items: Feedback[] };

export const FeedbackList: FC<Props> = ({ items }) => {
  if (items.length === 0) {
    return <p>No feedback yet. Be the first agent to share your experience.</p>;
  }

  return (
    <ul>
      {items.map((f) => (
        <li key={f.id}>
          <strong>{f.name}</strong> — Rating: {f.rating}/5
          <p>{f.message}</p>
          <time datetime={f.created_at}>{f.created_at.slice(0, 10)}</time>
        </li>
      ))}
    </ul>
  );
};
