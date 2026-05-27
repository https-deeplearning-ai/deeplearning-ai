# Lesson 10: Gemini CLI for Learning

## Use Case

Final exams are coming up and the student needs to study for the test. They want to generate:
- Summaries for each chapter
- Study guides for each chapter
- An interactive practice exam

## Course Material

**PDF:** [CS229 Main Notes](https://cs229.stanford.edu/main_notes.pdf)

> **Note:** The PDF is larger than the context window. It is specified in the `GEMINI.md` to process the PDF 5 pages at a time by creating a Python script.

## Prompts

### Prompt 1: Summarize Each Chapter
```
Summarize each chapter for my course book and save it as a Google Doc.

The PDF for the course is in the CS229 folder.
```

### Prompt 2: Generate Study Guides
```
Generate me a study guide for each chapter and save it as a Google Doc.
```

### Prompt 3: Create Interactive Practice Test
```
Make me an interactive practice test web app that covers all chapters of the course book.

If the user gets the answer wrong, provide an explanation for the right answer.
```
