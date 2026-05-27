# Lesson 7: Gemini CLI for Software Development

## Use Case

The schedule and list of speakers has been finalized for the conference. You have been tasked with a feature request to populate the session catalog page on the conference website.

## Getting Started

### Setup
```bash
npm install
npm run dev
```

## Custom Slash Commands

Custom slash commands let you define reusable prompts. You can:
- Pass arguments
- Execute shell commands

This is great for tasks you do often and don't want to type out a long prompt every time—like pulling information from GitHub and kicking off a bug fix or feature implementation.

## Prompts

### Prompt 1: Implement Feature
```
/implement-feature 5
```

## Shell Mode

Shell mode lets you quickly run commands without leaving Gemini CLI. Prefix commands with `!`:

### Running Tests
```
! npm run tests
```

### Committing Changes
```
! git commit
```

## Session Management

If you accidentally exit Gemini CLI, resume your previous session:
```bash
gemini --resume
```

## GitHub Integration

### GitHub Action for PR Review
Set up a GitHub Action to automatically review pull requests.

### Quick Setup
```
/setup-github
```
> This command helps you easily configure GitHub integration for your project.
