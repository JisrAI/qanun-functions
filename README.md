# Document Sync Azure Functions

This project contains Azure Functions for syncing documents to Elasticsearch using a serverless architecture.

## Functions

1. `sync-documents` - HTTP trigger function that receives documents and queues them for processing
2. `process-documents` - Queue trigger function that processes document batches and indexes them in Elasticsearch

## Local Development

### Prerequisites

1. Python 3.9 or later
2. Azure Functions Core Tools v4
3. Azure Storage Emulator or Azurite
4. Visual Studio Code with Azure Functions extension (optional)

### Setup

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure local settings:
   - Copy `local.settings.json` and update values as needed
   - Ensure Azure Storage Emulator is running for local queue storage

4. Run the functions locally:
```bash
func start
```

## Deployment

### Option 1: GitHub Actions (Recommended)

This project includes a GitHub Actions workflow for automated deployment. To use it:

1. Create a new Function App in Azure:
   - Runtime stack: Python
   - Version: 3.9 or later
   - Operating System: Linux
   - Plan type: Consumption (Serverless)

2. Configure application settings in Azure Portal:
   - ES_URL: Elasticsearch URL
   - ELASTIC_API_KEY: API key for Elasticsearch
   - ELASTIC_CLOUD_ID: Cloud ID for Elasticsearch
   - ELASTIC_VERIFY_CERTS: "true"

3. Get the publish profile:
   - Go to your Function App in Azure Portal
   - Click on "Get publish profile"
   - Copy the entire content

4. Add the publish profile to GitHub secrets:
   - Go to your GitHub repository settings
   - Navigate to Secrets and variables > Actions
   - Create a new secret named `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Paste the publish profile content

5. The workflow will automatically deploy when you push changes to the `main` branch.
   You can also manually trigger the workflow from the Actions tab.

### Option 2: Manual Deployment

1. Using Azure Functions Core Tools:
```bash
func azure functionapp publish <app-name>
```

2. Using VS Code:
   - Install Azure Functions extension
   - Right-click on the project folder
   - Select "Deploy to Function App..."
   - Follow the prompts

### Usage

Send documents to the sync endpoint:

```bash
curl -X POST https://<app-name>.azurewebsites.net/api/documents/sync \
  -H "Content-Type: application/json" \
  -H "x-functions-key: <function-key>" \
  -d '[
    {
      "doc_id": "example_1",
      "title": "Example Document",
      ...
    }
  ]'
```

The documents will be queued and processed in batches of 50, then indexed in Elasticsearch.

## Monitoring

- View function logs in Azure Portal
- Use Application Insights for detailed monitoring
- Check Azure Storage Queue metrics for queue processing stats
- Monitor Elasticsearch indexing through Elasticsearch logs and metrics

## Error Handling

- Failed document processing will be retried up to 5 times (configurable in host.json)
- Errors are logged to Application Insights
- Failed documents are logged with their error details
