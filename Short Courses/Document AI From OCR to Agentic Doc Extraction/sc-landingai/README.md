# Lab 6: Building a Research Paper Chatbot with Strands Agents

## Resources

This lab uses several AWS services including Lambda, S3, IAM, and Bedrock. To learn more about cloud computing on AWS, please check out the following resources: 

 * <u> **Documentation** </u>
    * <a href="https://docs.aws.amazon.com/s3/" target="_blank" style="text-decoration: none;">S3</a>
    * <a href="https://docs.aws.amazon.com/lambda/" target="_blank" style="text-decoration: none;">Lambda</a>
    * <a href="https://docs.aws.amazon.com/iam/" target="_blank" style="text-decoration: none;">IAM</a>
    * <a href="https://docs.aws.amazon.com/bedrock/" target="_blank" style="text-decoration: none;">Bedrock</a>
  * <u> **Libraries** </u>
    * <a href="https://docs.aws.amazon.com/pythonsdk/" target="_blank" style="text-decoration: none;">boto3</a>
    * <a href="https://docs.aws.amazon.com/bedrock-agentcore/" target="_blank" style="text-decoration: none;">bedrock-agentcore</a>
    * <a href="https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/strands-agents.html" target="_blank" style="text-decoration: none;">strands-agents</a>


## Overview

The pipeline consists of three components:

### 1. Document Processing 
- **S3 Bucket**: Stores uploaded PDF documents
- **Lambda Function**: Automatically triggered on file upload to S3
- **LandingAI ADE**:
    - Processes documents and extracts chunks with bounding boxes.
    - Creates individual JSON files for each document chunk
- **Storage**:
  - `output/medical/`: Markdown files
  - `output/medical_grounding/`: Grounding data with bounding boxes
  - `output/medical_chunks/`: Individual chunk JSON files for Knowledge Base
  - `output/medical_chunk_images/`: Dynamically generated cropped chunk images

### 2. Knowledge Base 
- **AWS Bedrock Knowledge Base**: Indexes individual chunk JSON files
- **Metadata**: Maintains chunk type, page number, and bounding box coordinates

### 3. Chatbot
- **Strands Agent Framework**: Orchestrates conversation flow
- **Bedrock Memory Service**: Maintains conversation context
- **Visual Grounding**: 
  - Extracts and crops specific chunk regions from PDFs
  - Adds red border highlighting around chunks

## Dependencies

To replicate the lab, you must configure your own AWS account. 

- Python
    - Use version 3.10 
- OS
    - Recommended to use x86_64
- AWS
    - Please get AWS account with permissions for the following service
        - Lambda
        - S3
        - IAM
        - Bedrock
        - CloudWatch Logs
      - In your account you must set up the following resources
        - S3 Bucket 
        - Bedrock Knowledge Base 
- LandingAI
    - Vision Agent API Key
    - Remember that you can make a free account at <a href="https://bit.ly/3Ys8HXL" target="_blank">LandingAI</a>: 

## Folder Structure

```
sc-landingai/
├── L6.ipynb                          # Main lab notebook
├── ade_s3_handler.py                 # Lambda function for document processing
├── lambda_helpers.py                 # Helper functions for Lambda deployment
├── visual_grounding_helper.py        # Functions for creating cropped chunk images
├── medical/                          # Sample medical PDF documents
│   ├── Common_cold_clinincal_evidence.pdf
│   ├── CT_Study_of_the_Common_Cold.pdf
│   ├── Evaluation_of_echinacea_for_the_prevention_and_treatment_of_the_common_cold.pdf
│   ├── Prevention_and_treatment_of_the_common_cold.pdf
│   ├── The_common_cold_a_review_of_the_literature.pdf
│   ├── Understanding_the_symptoms_of_the_common_cold_and_influenza.pdf
│   ├── Viruses_and_Bacteria_in_the_Etiology_of_the_Common_Cold.pdf
│   └── Vitamin_C_for_Preventing_and_Treating_the_Common_Cold.pdf
└── README.md                         # This file
```

##  Getting Started

### Step 0: S3 and Bedrock

- Make two folders in your S3 bucket called `input/` and `output/`
- Connect the Bedrock Knowledge Base to the folder

### Step 1: Environment Setup

Create a `.env` file with your credentials:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
S3_BUCKET=your-bucket-name
VISION_AGENT_API_KEY=your_landingai_api_key
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_KB_ID=your_knowledge_base_id
```

### Step 2: Install Dependencies

```bash
pip install boto3 python-dotenv Pillow PyMuPDF landingai-ade typing-extensions
pip install bedrock-agentcore strands-agents pandas
```

### Step 3: Run the Notebook

Open `Lab-6.ipynb` in Jupyter and follow the step-by-step instructions to:
1. Deploy the Lambda function
2. Set up S3 triggers
3. Process medical documents (creates chunks automatically)
4. Configure Bedrock Knowledge Base to index `output/medical_chunks/`
5. Test chunk-based search with `search_medical_chunks()`
6. Launch the interactive chatbot

## Monitoring & Debugging

### CloudWatch Logs
Monitor Lambda execution in AWS CloudWatch:
- Processing status for each document
- Error messages and stack traces
- Performance metrics and duration

### S3 Output Verification
Check processed outputs:
```python
# List all processed files
stats = monitor_lambda_processing(logs_client, s3_client, bucket_name)
```

### Knowledge Base Sync
Verify document ingestion:
```python
response = bedrock_agent.start_ingestion_job(
    knowledgeBaseId=BEDROCK_KB_ID,
    dataSourceId=DATA_SOURCE_ID
)
```

## Troubleshooting

### Common Issues

1. **Lambda Timeout**: Increase timeout in deployment (default: 900s)
2. **Memory Errors**: Increase Lambda memory (default: 1024MB)
3. **IAM Permissions**: Ensure role has S3 and CloudWatch access
4. **Python Version Mismatch**: Use Python 3.10 for compatibility
5. **Knowledge Base Not Found**: Verify KB ID and region settings

### Debug Commands

```python
# Check Lambda logs
monitor_lambda_processing(logs_client, s3_client, bucket)

# Verify S3 outputs
s3_client.list_objects_v2(Bucket=bucket, Prefix='output/')

# Test chunk-based search
results = search_medical_chunks("test query", s3_client, bucket)

# Test knowledge base search
test_result = search_knowledge_base("test query")
```

**⚠️ Note**: This lab requires active AWS services which may incur costs. Remember to clean up resources after completing the exercises.