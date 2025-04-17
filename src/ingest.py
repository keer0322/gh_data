from fastapi import FastAPI, Request, Header, HTTPException
from google.cloud import storage
import hmac
import hashlib
import os
import json
import datetime
import uuid

app = FastAPI()

# GCS bucket config
GCS_BUCKET = os.getenv("GCS_BUCKET", "github-webhook-raw")
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Init GCS client
gcs_client = storage.Client()
bucket = gcs_client.bucket(GCS_BUCKET)

def verify_signature(payload_body, signature, secret):
    mac = hmac.new(secret.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    body = await request.body()

    if WEBHOOK_SECRET and not verify_signature(body, x_hub_signature_256, WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()

    # Filter only Actions-related events
    tracked_events = ["workflow_run", "workflow_job", "check_run", "check_suite"]
    if x_github_event not in tracked_events:
        return {"status": "ignored", "event": x_github_event}

    # Save raw JSON to GCS
    now = datetime.datetime.utcnow().isoformat()
    filename = f"github-events/{x_github_event}/{now}_{uuid.uuid4()}.json"
    blob = bucket.blob(filename)
    blob.upload_from_string(json.dumps(payload), content_type='application/json')

    return {"status": "stored", "filename": filename}
