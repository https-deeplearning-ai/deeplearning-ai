# Lesson 8: Gemini CLI for Data Analysis

## Use Case

The team just got back from the conference and have the lead scan data from every session and booth. You need to:
1. Consolidate and clean the data
2. Deduplicate and assign lead scores
3. Create a comprehensive report
4. Build an interactive dashboard with visualizations and filters

## Prompts

### Prompt 1: Consolidate and Clean Data
```
I have conference lead scan data locally and also on Google Sheets. The local data is in a directory named `lead-scan` containing multiple CSV files. The data on Google Sheets is in a folder named Techstack Conference.

Please process and clean this data into a revenue-ready format. Save the final cleaned dataset to crm_import_ready.csv.
```

<details>
<summary>Alternative (without Google Sheets)</summary>

```
I have a directory named `lead-scan` containing multiple CSV files of conference lead scans. Please process and clean this data into a revenue-ready format. Save the final cleaned dataset to crm_import_ready.csv.
```
</details>

### Prompt 2: Import to Database
```
Import the data from @crm_import_ready.csv to a BigQuery database on Google Cloud.
```

### Prompt 3: Query the Data
```
Can you query how many warm leads we have using the BigQuery table?
```

### Prompt 4: Deep Analysis and Report
```
Please do a deep analysis of the lead scan data to find trends and important details that will be beneficial to our future marketing plan.

Compile a detailed report with core metrics in Google Docs.
```

### Adding Website Directory for Branding
```
/dir add ../website
```

### Prompt 5: Build Dashboard
```
Build a Flask dashboard to visualize the clean lead scan dataset.

Use brand colors and conference logo from website.
```

### Prompt 6: Start Dashboard
```
Start the dashboard in the foreground.
```

> **Note:** You must specify "foreground" because it will automatically start in the background and the webapp doesn't load.

## Other Use Cases

- Analyzing sensitive information that is local to your environment
- Cloud Data Ops & Infrastructure Management to manage resources used for queries

## Useful Extensions for Data Analysts

### Database Extensions
| Extension | Description |
|-----------|-------------|
| `mysql` | MySQL database integration |
| `postgres` | PostgreSQL database integration |
| `cloud-sql-postgresql` | Google Cloud SQL for PostgreSQL |
| `cloud-sql-mysql` | Google Cloud SQL for MySQL |
| `bigquery-data-analytics` | BigQuery data analytics |
| `alloydb` | AlloyDB integration |
| `looker` | Looker visualization |
