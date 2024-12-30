import logging
import json
import os
import azure.functions as func
import requests
from typing import List, Dict, Any

# Elasticsearch configuration
ES_URL = os.environ["ES_URL"]
ELASTIC_API_KEY = os.environ["ELASTIC_API_KEY"]
INDEX_NAME = "legal_documents.documents"

# Configure headers with API key
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {ELASTIC_API_KEY}"
}

def bulk_index_documents(documents: List[Dict[str, Any]], batch_id: str) -> Dict[str, Any]:
    """Index a batch of documents using the Elasticsearch bulk API."""
    if not documents:
        return {"indexed": 0, "failed": 0, "errors": []}

    # Prepare bulk request body
    bulk_body = []
    for doc in documents:
        # Add index action
        bulk_body.append(json.dumps({
            "index": {
                "_index": INDEX_NAME,
                "_id": doc["doc_id"]
            }
        }))
        # Add document data
        bulk_body.append(json.dumps(doc))

    bulk_data = "\n".join(bulk_body) + "\n"

    try:
        response = requests.post(
            f"{ES_URL}/_bulk",
            headers=HEADERS,
            data=bulk_data,
            verify=True  # For Azure, always verify SSL
        )
        
        result = response.json()
        
        if result.get("errors", False):
            failed_items = [
                item for item in result["items"]
                if item.get("index", {}).get("status", 200) >= 400
            ]
            
            if failed_items:
                failed_ids = [item["index"]["_id"] for item in failed_items]
                errors = [
                    {
                        "id": item["index"]["_id"],
                        "error": item["index"]["error"]
                    }
                    for item in failed_items
                ]
                
                logging.error(
                    f"Batch {batch_id}: Failed to index documents: {failed_ids}\n"
                    f"Errors: {errors}"
                )
                
                return {
                    "indexed": len(documents) - len(failed_items),
                    "failed": len(failed_items),
                    "errors": errors
                }
            else:
                return {
                    "indexed": len(documents),
                    "failed": 0,
                    "errors": []
                }
        else:
            return {
                "indexed": len(documents),
                "failed": 0,
                "errors": []
            }

    except Exception as e:
        logging.error(f"Batch {batch_id}: Error during bulk indexing: {str(e)}")
        return {
            "indexed": 0,
            "failed": len(documents),
            "errors": [{"error": str(e)}]
        }

def main(msg: func.QueueMessage) -> None:
    try:
        # Parse queue message
        message_body = msg.get_body().decode('utf-8')
        batch_data = json.loads(message_body)
        
        # Extract batch information
        batch_id = batch_data.get("batch_id")
        total_batches = batch_data.get("total_batches")
        documents = batch_data.get("documents", [])
        
        logging.info(f"Processing batch {batch_id} of {total_batches} with {len(documents)} documents")
        
        # Index documents
        result = bulk_index_documents(documents, batch_id)
        
        # Log results
        logging.info(
            f"Batch {batch_id} complete:\n"
            f"- Documents indexed: {result['indexed']}\n"
            f"- Documents failed: {result['failed']}"
        )
        
        if result["errors"]:
            logging.error(f"Batch {batch_id} errors: {json.dumps(result['errors'], indent=2)}")
        
    except Exception as e:
        logging.error(f"Error processing queue message: {str(e)}")
        raise  # Re-raise to trigger Azure Functions retry policy
