# Qanun Functions

Azure Functions for efficient document syncing to Elasticsearch. This serverless solution handles batch processing of legal documents with reliable queueing and error handling.

## Project Structure

```
qanun-functions/
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions deployment workflow
├── sync-documents/         # HTTP trigger function
│   ├── function.json      # Function bindings
│   └── __init__.py        # Function implementation
├── process-documents/      # Queue trigger function
│   ├── function.json      # Function bindings
│   └── __init__.py        # Function implementation
├── host.json              # Function app settings
├── local.settings.json    # Local development settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Features

- HTTP endpoint for document ingestion
- Queue-based batch processing
- Efficient Elasticsearch bulk indexing
- Error handling with retries
- Monitoring and logging
- GitHub Actions automated deployment

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
   - Copy `local.settings.json.example` to `local.settings.json`
   - Update the following settings:
     ```json
     {
       "IsEncrypted": false,
       "Values": {
         "AzureWebJobsStorage": "UseDevelopmentStorage=true",
         "FUNCTIONS_WORKER_RUNTIME": "python",
         "ES_URL": "your-elasticsearch-url",
         "ELASTIC_API_KEY": "your-api-key",
         "ELASTIC_CLOUD_ID": "your-cloud-id",
         "ELASTIC_VERIFY_CERTS": "true"
       }
     }
     ```

4. Run the functions locally:
```bash
func start
```

## Deployment

### Option 1: GitHub Actions (Recommended)

This repository includes a GitHub Actions workflow for automated deployment:

1. Create a new Function App in Azure:
   - Runtime stack: Python
   - Version: 3.9 or later
   - Operating System: Linux
   - Plan type: Consumption (Serverless)

2. Configure application settings in Azure Portal with the same settings as in local.settings.json

3. Add your publish profile to GitHub secrets:
   - Get the publish profile from Azure Portal
   - Add it as `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` in repository secrets

4. The workflow will automatically deploy when you push to main

### Option 2: Manual Deployment

```bash
func azure functionapp publish <app-name>
```

## API Usage

### Sync Documents

```bash
curl -X POST https://<app-name>.azurewebsites.net/api/documents/sync \
  -H "Content-Type: application/json" \
  -H "x-functions-key: <function-key>" \
  -d '[
    {
      "doc_id": "example_1",
      "title": {
        "ar": "عنوان المستند",
        "en": "Document Title"
      },
      "date": "2024-01-01",
      "paragraphs": [
        {
          "text": {
            "ar": "نص الفقرة",
            "en": "Paragraph text"
          }
        }
      ]
    }
  ]'
```

Response:
```json
{
  "status": "success",
  "message": "Queued 1 documents for indexing",
  "total_batches": 1
}
```

## Monitoring

- View function logs in Azure Portal
- Use Application Insights for detailed monitoring
- Check Azure Storage Queue metrics for queue processing stats
- Monitor Elasticsearch indexing through Elasticsearch logs and metrics

## Error Handling

- Failed document processing will be retried up to 5 times
- Errors are logged to Application Insights
- Failed documents are logged with their error details
- Queue visibility timeout ensures no lost messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
