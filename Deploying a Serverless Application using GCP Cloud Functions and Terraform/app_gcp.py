# app_gcp.py
# Cloud Functions compatible handler (HTTP-triggered)
from google.cloud import storage
from google.cloud import firestore
from flask import Request

storage_client = storage.Client()
firestore_client = firestore.Client()


def lambda_handler(request: Request):
    # Write a simple object to a Storage bucket
    bucket_name = 'sample-function-bucket'
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob('hello.txt')
        blob.upload_from_string('Hello, World!')
    except Exception:
        # If storage isn't available or bucket missing, continue
        pass

    # Write a simple doc to Firestore
    try:
        doc_ref = firestore_client.collection('sample-collection').document('test')
        doc_ref.set({'name': 'John', 'age': 30})
    except Exception:
        pass

    name = None
    if isinstance(request, dict):
        name = request.get('name', 'World')
    else:
        try:
            req_json = request.get_json(silent=True)
            name = req_json.get('name') if req_json else request.args.get('name', 'World')
        except Exception:
            name = 'World'

    return (f'Hello, {name}!', 200)
