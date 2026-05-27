# Skills with the Claude API

## Lesson Files

You can find the lesson's notebook and all the required input files <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L5" target="_blank">here</a>.

To run the notebook, you need to create a `.env` file containing an Anthropic API key (no Claude subscription is required):

`ANTHROPIC_API_KEY="your-key"`

You can get a key from <a href="https://platform.claude.com/dashboard" target="_blank">Claude Developer Platform</a>. 

**About costs:** Please note that running through all the notebook cells once will use approximately $0.67 in API credits. 

If you'd prefer not to run the notebook, you can:
- view the <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L5/lesson_5.ipynb" target="_blank">notebook with pre-run outputs</a> (exactly as shown in the video)
- check out the <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L5/sample_outputs/" target="_blank">generated sample outputs</a>

You can also try the same custom skills in Claude.ai.

## Notes
- Here's the <a href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#pre-installed-libraries" target="_blank">list of pre-installed libraries in the sandboxed environment</a>
- Streaming: The lesson's notebook does not implement streaming with the Messages API. So when you run the cells to get the response, you might need to wait for a few minutes. If you'd like to implement streaming, you can check the documentation <a href="https://platform.claude.com/docs/en/build-with-claude/streaming" target="_blank">here</a>.
- To see more examples of how to use Agent Skills with the API (like multi-turn conversation), make sure to check this <a href="https://platform.claude.com/docs/en/build-with-claude/skills-guide" target="_blank">guide</a>.

## Additional References
- <a href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool" target="_blank">Code Execution Tool</a>
- <a href="https://platform.claude.com/docs/en/build-with-claude/files" target="_blank">Files API</a>
- <a href="https://github.com/anthropics/claude-cookbooks/tree/main/skills" target="_blank">Claude Cookbook: Skills</a>