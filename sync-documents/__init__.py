import logging
import json
import azure.functions as func
from typing import List, Dict, Any

def main(req: func.HttpRequest, outputQueueItem: func.Out[str]) -> func.HttpResponse:
    logging.info('Document sync request received')

    try:
        # Get request body
        req_body = req.get_json()
        
        # Validate request body
        if not isinstance(req_body, list):
            return func.HttpResponse(
                json.dumps({"error": "Request body must be an array of documents"}),
                mimetype="application/json",
                status_code=400
            )

        # Queue documents in batches of 50
        batch_size = 50
        total_queued = 0
        
        for i in range(0, len(req_body), batch_size):
            batch = req_body[i:i + batch_size]
            # Add batch metadata
            batch_data = {
                "batch_id": f"batch_{i//batch_size}",
                "total_batches": (len(req_body) + batch_size - 1) // batch_size,
                "batch_size": len(batch),
                "documents": batch
            }
            
            # Queue the batch
            outputQueueItem.set(json.dumps(batch_data))
            total_queued += len(batch)

        return func.HttpResponse(
            json.dumps({
                "status": "success",
                "message": f"Queued {total_queued} documents for indexing",
                "total_batches": (len(req_body) + batch_size - 1) // batch_size
            }),
            mimetype="application/json"
        )

    except ValueError as ve:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
