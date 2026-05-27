import { describe, it, expect } from "vitest";
import { Header } from "../src/components/Header";
import { Footer } from "../src/components/Footer";
import { Main } from "../src/components/Main";
import { Layout } from "../src/components/Layout";
import { FeedbackForm } from "../src/components/FeedbackForm";
import { FeedbackList } from "../src/components/FeedbackList";
import type { Feedback } from "../src/db/types";

describe("Header", () => {
  it("renders a header element", () => {
    const html = Header({}).toString();
    expect(html).toContain("<header");
  });

  it("links to the home page", () => {
    const html = Header({}).toString();
    expect(html).toContain('href="/"');
  });

  it("displays the site name", () => {
    const html = Header({}).toString();
    expect(html).toContain("AgentClinic");
  });
});

describe("Footer", () => {
  it("renders a footer element", () => {
    const html = Footer({}).toString();
    expect(html).toContain("<footer");
  });

  it("displays the current year", () => {
    const html = Footer({}).toString();
    expect(html).toContain(String(new Date().getFullYear()));
  });

  it("displays the site name", () => {
    const html = Footer({}).toString();
    expect(html).toContain("AgentClinic");
  });
});

describe("Main", () => {
  it("renders a main element", () => {
    const html = Main({ children: "content" }).toString();
    expect(html).toContain("<main");
  });

  it("renders children", () => {
    const html = Main({ children: "hello world" }).toString();
    expect(html).toContain("hello world");
  });
});

describe("Layout", () => {
  it("renders an html element with lang attribute", () => {
    const html = Layout({ children: "" }).toString();
    expect(html).toContain('<html lang="en"');
  });

  it("includes a title", () => {
    const html = Layout({ children: "" }).toString();
    expect(html).toContain("<title>AgentClinic</title>");
  });

  it("links the stylesheet", () => {
    const html = Layout({ children: "" }).toString();
    expect(html).toContain('href="/static/style.css"');
  });

  it("renders children", () => {
    const html = Layout({ children: "page content" }).toString();
    expect(html).toContain("page content");
  });

  it("includes header and footer", () => {
    const html = Layout({ children: "" }).toString();
    expect(html).toContain("<header");
    expect(html).toContain("<footer");
  });

  it("includes the viewport meta tag for responsive design", () => {
    const html = Layout({ children: "" }).toString();
    expect(html).toContain('name="viewport"');
    expect(html).toContain("width=device-width");
  });
});

describe("FeedbackForm", () => {
  it("renders all four fields", () => {
    const html = FeedbackForm({}).toString();
    expect(html).toContain('name="name"');
    expect(html).toContain('name="email"');
    expect(html).toContain('name="message"');
    expect(html).toContain('name="rating"');
  });

  it("posts to /feedback", () => {
    const html = FeedbackForm({}).toString();
    expect(html).toContain('action="/feedback"');
    expect(html).toContain('method="post"');
  });

  it("renders error messages when provided", () => {
    const html = FeedbackForm({ errors: { name: "Agent ID is required." } }).toString();
    expect(html).toContain("Agent ID is required.");
  });
});

describe("FeedbackList", () => {
  const sampleItem: Feedback = {
    id: 1,
    name: "TestBot-1",
    email: null,
    message: "Very helpful.",
    rating: 5,
    created_at: "2026-04-06 12:00:00",
  };

  it("renders a list when given items", () => {
    const html = FeedbackList({ items: [sampleItem] }).toString();
    expect(html).toContain("TestBot-1");
    expect(html).toContain("Very helpful.");
    expect(html).toContain("5");
  });

  it("renders the empty-state message when given an empty array", () => {
    const html = FeedbackList({ items: [] }).toString();
    expect(html).toContain("No feedback yet");
  });
});
