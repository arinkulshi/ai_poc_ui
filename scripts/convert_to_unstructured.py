"""
Convert structured email JSONL to individual HTML files for
Discovery Engine unstructured data ingestion.

Usage:
    python scripts/convert_to_unstructured.py <input_jsonl> <output_dir>

Example:
    python scripts/convert_to_unstructured.py \
        ../output_jsonl/emails_part_001.jsonl \
        ../output_unstructured/part_001

This produces:
  - output_dir/docs/     -> Individual HTML files (one per email)
  - output_dir/metadata.jsonl -> Metadata JSONL for Discovery Engine import
                                 (update GCS bucket path before use)
"""

import json
import os
import sys
import html
from pathlib import Path


GCS_BUCKET_PLACEHOLDER = "gs://eron_unstructure/unstructured"


def email_to_html(record: dict) -> str:
    """Convert a single email record to an HTML document."""
    data = record.get("structData", {})

    subject = html.escape(data.get("subject", "(No Subject)") or "(No Subject)")
    sender = html.escape(data.get("sender_name", data.get("sender", "Unknown")))
    sender_email = html.escape(data.get("sender", ""))
    to = html.escape(data.get("to_name", data.get("to", "Unknown")))
    to_email = html.escape(data.get("to", ""))
    cc = html.escape(data.get("cc", ""))
    date = html.escape(data.get("date", ""))
    body = html.escape(data.get("body", "")).replace("\n", "<br>\n")
    folder = html.escape(data.get("folder", ""))
    origin = html.escape(data.get("origin", ""))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{subject}</title>
</head>
<body>
<h1>{subject}</h1>
<table>
<tr><td><strong>From:</strong></td><td>{sender} &lt;{sender_email}&gt;</td></tr>
<tr><td><strong>To:</strong></td><td>{to} &lt;{to_email}&gt;</td></tr>
{"<tr><td><strong>CC:</strong></td><td>" + cc + "</td></tr>" if cc else ""}
<tr><td><strong>Date:</strong></td><td>{date}</td></tr>
<tr><td><strong>Folder:</strong></td><td>{folder}</td></tr>
<tr><td><strong>Origin:</strong></td><td>{origin}</td></tr>
</table>
<hr>
<div class="body">
{body}
</div>
</body>
</html>"""


def convert_file(input_path: str, output_dir: str):
    """Convert a JSONL file to individual HTML documents + metadata JSONL."""
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = output_dir / "metadata.jsonl"
    part_name = input_path.stem  # e.g. "emails_part_001"

    count = 0
    with open(input_path, "r") as infile, open(metadata_path, "w") as meta_file:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            doc_id = record["id"]
            filename = f"{doc_id}.html"

            # Write HTML file
            html_content = email_to_html(record)
            doc_path = docs_dir / filename
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Write metadata entry for Discovery Engine import
            # The URI should point to where you upload the file in GCS
            gcs_uri = f"{GCS_BUCKET_PLACEHOLDER}/{part_name}/{filename}"
            meta_entry = {
                "id": doc_id,
                "content": {
                    "mimeType": "text/html",
                    "uri": gcs_uri,
                },
                "structData": {
                    "sender": record["structData"].get("sender", ""),
                    "sender_name": record["structData"].get("sender_name", ""),
                    "to": record["structData"].get("to", ""),
                    "subject": record["structData"].get("subject", ""),
                    "date": record["structData"].get("date", ""),
                    "folder": record["structData"].get("folder", ""),
                    "origin": record["structData"].get("origin", ""),
                },
            }
            meta_file.write(json.dumps(meta_entry) + "\n")

            count += 1
            if count % 10000 == 0:
                print(f"  Processed {count} documents...")

    print(f"Done! Converted {count} emails.")
    print(f"  HTML files: {docs_dir}/")
    print(f"  Metadata:   {metadata_path}")
    print()
    print("Next steps:")
    print(f"  1. Upload HTML files to GCS:")
    print(f"     gsutil -m cp -r {docs_dir}/* {GCS_BUCKET_PLACEHOLDER}/{part_name}/")
    print(f"  2. Update the bucket path in {metadata_path} if different")
    print(f"  3. Upload metadata to GCS:")
    print(f"     gsutil cp {metadata_path} {GCS_BUCKET_PLACEHOLDER}/{part_name}_metadata.jsonl")
    print(f"  4. Import into Discovery Engine as unstructured data using the metadata JSONL")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <input_jsonl> <output_dir>")
        print(f"Example: python {sys.argv[0]} ../output_jsonl/emails_part_001.jsonl ../output_unstructured/part_001")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Converting: {input_file}")
    print(f"Output to:  {output_directory}")
    print()
    convert_file(input_file, output_directory)
