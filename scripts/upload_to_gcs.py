"""Upload unstructured HTML files and metadata to GCS."""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
BUCKET_NAME = "eron_unstructure"
GCS_PREFIX = "unstructured/emails_part_001"


def upload_file(client, bucket, local_path, gcs_path):
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(str(local_path), content_type="text/html")
    return gcs_path


def main():
    docs_dir = Path("/Users/arindamkulshi/ai_poc_ui/output_unstructured/docs")
    metadata_path = Path("/Users/arindamkulshi/ai_poc_ui/output_unstructured/part_001/metadata.jsonl")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(CREDENTIALS_PATH)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # Collect all HTML files
    html_files = list(docs_dir.glob("*.html"))
    total = len(html_files)
    print(f"Found {total} HTML files to upload")

    # Upload HTML files in parallel
    uploaded = 0
    errors = 0
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {}
        for f in html_files:
            gcs_path = f"{GCS_PREFIX}/{f.name}"
            future = executor.submit(upload_file, client, bucket, f, gcs_path)
            futures[future] = f.name

        for future in as_completed(futures):
            try:
                future.result()
                uploaded += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error uploading {futures[future]}: {e}")

            if uploaded % 5000 == 0:
                print(f"  Uploaded {uploaded}/{total} files...")

    print(f"HTML upload complete: {uploaded} succeeded, {errors} errors")

    # Upload metadata JSONL
    print(f"Uploading metadata.jsonl...")
    meta_blob = bucket.blob(f"{GCS_PREFIX}_metadata.jsonl")
    meta_blob.upload_from_filename(str(metadata_path), content_type="application/jsonl")
    print(f"Metadata uploaded to gs://{BUCKET_NAME}/{GCS_PREFIX}_metadata.jsonl")

    print("\nDone! All files uploaded to GCS.")


if __name__ == "__main__":
    main()
