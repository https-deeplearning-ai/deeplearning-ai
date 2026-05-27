# Exploring Pre-Built Skills

## Pre-Built Skills

* <a href="https://github.com/anthropics/skills/tree/main/skills" target="_blank">List of Anthropic skills</a>
* <a href="https://github.com/anthropics/skills/tree/main/skills/pptx" target="_blank">pptx</a>
* <a href="https://github.com/anthropics/skills/tree/main/skills/skill-creator" target="_blank">Skill creator</a>

## Part 1: Updating the Marketing Skill

In the video, we updated the Marketing skill to use the BigQuery MCP server to get data from a BigQuery table instead of requiring a CSV file:

- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/prompts.md#part-1-updating-the-marketing-skill" target="_blank">Prompts used in this part 1</a>
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/updated_marketing_skill/analyzing-marketing-campaign/" target="_blank">Updated files of the Marketing skill obtained during filming</a>

You can set up a BigQuery table to try this part (link to instructions below), or you can set up a local database instead. For example, you can set up a local SQLite database, import this <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/campaign_performance_4weeks.csv" target="_blank">CSV file</a> into the database, and use this <a href="https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite" target="_blank">MCP server</a>. Or you can skip this part entirely.

- Optional: <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/additional_references/table_setup.md#bigquery-setup" target="_blank">Instructions for setting up a BigQuery table</a>
- Optional alternative: <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/additional_references/table_setup.md#sqlite-setup" target="_blank">Instructions for setting up a SQLite table</a>

**Note**: Since BigQuery MCP Server is a local MCP server, we used Claude Desktop (not Claude.ai). With Claude.ai, you can only use remote MCP servers.

## Part 2: Creating the Brand Guidelines Skill

- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/brand_guidelines_files/" target="_blank">Brand guidelines files</a>
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/prompts.md#part-2--creating-the-brand-guideline-skill" target="_blank">Prompts used in part 2</a>
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/brand_guidelines_skill/craftedwell-brand/" target="_blank">Files of the skill obtained during filming</a>

## Part 3: Implementing the Entire Workflow

- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/prompts.md#part-3-implementing-the-entire-workflow" target="_blank">Prompts used in part 3</a>
- <a href="https://github.com/https-deeplearning-ai/sc-agent-skills-files/tree/main/L3/output_report_example/CraftedWell_Weekly_Report_Dec16-22.pptx" target="_blank">Slides obtained during filming</a>

The slides might take a few minutes to generate, and they might look completely different from those in the video.