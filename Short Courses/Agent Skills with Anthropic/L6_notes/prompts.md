# Prompts

## Part 1: Adding the `edit command`
- Add a new CLI  edit command to allow users edit the title or priority of the task. For example: edit task 3 --title "New title". If users do not provide any options, then do not edit anything and exit with a message "no edits were done, specify title or priority". If edits are made, display the table of tasks. Make sure to follow the conventions for creating a new CLI command.

**Note:** When testing the skill, there were a few times when Claude Code decided not to use it. We worked on making the skill's description more detailed, but Claude might still decide not to use it. In that case, you can interrupt Claude Code and explicitly instruct it to use the skill by saying "Use skill X to...". Alternatively, you can use user-invoked mode in Claude Code by entering the skill as a command: `/name-of-the-skill + details`. For example: `/adding-cli-command + details of the command you want to add`. When you type a slash command like `/adding-cli-command`, the system automatically loads that skill's content into the conversation.

## Part 2: Setting up the subagents

The subagent definitions are provided directly in 
<a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L6/.claude/agents" target="_blank">the codebase</a>. If you'd like to set them up yourself, you can delete the existing files. Here are the system prompts for each subagent:
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/blob/main/L6/.claude/agents/code-reviewer.md?plain=1" target="_blank">Code reviewer subagent</a>
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/blob/main/L6/.claude/agents/test-generator-runner.md?plain=1" target="_blank">Test generator/runner subagent</a>

## Part 3: Using the subagents

- Use the code-reviewer subagent to review the `@edit.py` command.

- Use the test-generator-runner subagent to generate tests for the `@edit.py` command.

- Use the code-reviewer subagent to review the `@clear.py` command. Fix any issues, then use the test-generator-runner subagent to generate tests for the `@clear.py` command.