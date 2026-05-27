# Rules

* When processing and cleaning up lead scan data, follow the following rules:
  1. Consolidate & Deduplicate: Merge all files into a single dataset using 'Email' as the unique identifier.
  2. Conflict Resolution: If a lead appears multiple times, use the contact details (Name, Company, Phone) from the *most recent* 'Timestamp'.
  3. Aggregation: Combine all distinct 'Session ID' into a single list (semicolon-separated). Append all 'Notes' together. Keep the *highest* 'Lead Score' recorded for that person.
  4.  Validate: Filter out any rows where the 'Email' is missing or does not contain an '@' symbol and a domain extension. Report how many bad records were dropped.
  5.  Score & Segment: Create a new column named `Priority_Segment` based on their final 'Lead Score':
      * Hot: Score > 75
      * Warm: Score between 40 and 75
      * Cold: Score < 40

* When making an analysis report, make sure it is professional and executive ready. The report must include:
  1. Executive Summary: High-level overview of the results.
  2. Methodology: Brief explanation of the cleaning/scoring logic.
  3. Audience Insights: Analyze the audience data and give a summary of the findings. Also list the Top 5 Companies, Top Countries, and Top Job Titles to identify who is attending.
  4. Conference Insights: Analyze the conference data and give a summary of the findings. Also list the Most attended sessions per session type and the popular session topics.
  5. Strategic Recommendations: Actionable advice for the sales team based on these insights (e.g., specific companies to target).
  6. Marketing Recommendations: Actionable advice for the marketing team based on these insights (e.g., specific job roles or topics to target)
  7. Key Metrics: The final counts for Total Raw Records, Unique Leads, Invalid Records, and the Hot/Warm/Cold breakdown.

* When building a dashboard for lead scan data, make sure to include:
  * Prefer using `pyproject.toml` and `uv` over `pip`
  * Overview Panel: Display key metrics (Total, Hot, Warm, Cold) using colorful cards.
  * Visualizations: Integrate Chart.js to show:
    * A Pie Chart for the Lead Segment distribution.
    * A Bar Chart for the Top 5 Companies.
    * A World Map (or simple list) highlighting top Countries.
  * Interactive List: A searchable and filterable table (by Region, Company, Title) that lets me click a lead to view their full profile.
