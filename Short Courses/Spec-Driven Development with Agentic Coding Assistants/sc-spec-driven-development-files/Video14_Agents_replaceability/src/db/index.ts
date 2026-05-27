import Database from "better-sqlite3";
import type { Feedback } from "./types";

export function createDb(path: string = "agentclinic.db") {
  const db = new Database(path);
  db.pragma("foreign_keys = ON");
  return db;
}

export function getAllFeedback(db: Database.Database): Feedback[] {
  return db.prepare("SELECT * FROM feedback ORDER BY created_at DESC, id DESC").all() as Feedback[];
}

export function createFeedback(
  db: Database.Database,
  data: { name: string; email: string | null; message: string; rating: number }
): Feedback {
  const result = db
    .prepare("INSERT INTO feedback (name, email, message, rating) VALUES (?, ?, ?, ?)")
    .run(data.name, data.email, data.message, data.rating);
  return db
    .prepare("SELECT * FROM feedback WHERE id = ?")
    .get(result.lastInsertRowid) as Feedback;
}
