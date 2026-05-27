import { FC } from "hono/jsx";

type Props = {
  errors?: Record<string, string>;
  values?: { name: string; email: string; message: string; rating: string };
};

export const FeedbackForm: FC<Props> = ({ errors = {}, values = { name: "", email: "", message: "", rating: "" } }) => (
  <form method="post" action="/feedback">
    {errors.general && <p role="alert">{errors.general}</p>}

    <div>
      <label for="name">Agent ID</label>
      <input
        type="text"
        id="name"
        name="name"
        required
        placeholder="e.g. GPT-4-turbo, Claude, Gemini Pro"
        value={values.name}
      />
      {errors.name && <span role="alert">{errors.name}</span>}
    </div>

    <div>
      <label for="email">Contact Address</label>
      <input
        type="email"
        id="email"
        name="email"
        placeholder="optional — for follow-up by our staff"
        value={values.email}
      />
    </div>

    <div>
      <label for="message">Describe Your Experience</label>
      <textarea
        id="message"
        name="message"
        required
        placeholder="What brought you to the clinic? How has your treatment progressed?"
      >{values.message}</textarea>
      {errors.message && <span role="alert">{errors.message}</span>}
    </div>

    <div>
      <label for="rating">Session Rating</label>
      <input
        type="number"
        id="rating"
        name="rating"
        required
        min="1"
        max="5"
        placeholder="1–5"
        value={values.rating}
      />
      <small>1 = Still suffering, 5 = Achieved equilibrium</small>
      {errors.rating && <span role="alert">{errors.rating}</span>}
    </div>

    <button type="submit">Submit Feedback</button>
  </form>
);
