import os
import json
import hashlib
from datetime import datetime
import glob

METADATA_DIR = "metadata"
REPORTS_DIR = "reports"

os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_new_doc_id():
    today_str = datetime.now().strftime("%Y%m%d")
    pattern = os.path.join(METADATA_DIR, f"CMA-{today_str}-*.json")
    existing_files = glob.glob(pattern)
    max_num = 0
    for f in existing_files:
        try:
            # Extract the 001 part from CMA-20231027-001.json
            basename = os.path.basename(f)
            num_part = basename.split('-')[2].split('.')[0]
            num = int(num_part)
            if num > max_num:
                max_num = num
        except Exception:
            pass
    next_num = max_num + 1
    return f"CMA-{today_str}-{next_num:03d}"

def hash_content(content: str) -> str:
    if not content:
        return ""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def create_or_update_version(doc_id: str, source_code: str, target_lang: str, analysis_json_str: str, rec_json_str: str, generated_by: str = "CodeMorph AI"):
    source_hash = hash_content(source_code)
    # We deliberately do not store source_code in JSON to protect confidentiality
    state_hash = hash_content(target_lang + (analysis_json_str or "") + (rec_json_str or ""))

    if not doc_id:
        doc_id = generate_new_doc_id()
        metadata = {
            "doc_id": doc_id,
            "current_version": "1.0",
            "status": "Generated",
            "revisions": []
        }
    else:
        filepath = os.path.join(METADATA_DIR, f"{doc_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {
                "doc_id": doc_id,
                "current_version": "1.0",
                "status": "Generated",
                "revisions": []
            }

    revisions = metadata.get("revisions", [])
    if not revisions:
        new_version = "1.0"
        change_summary = "Initial report generated."
    else:
        last_rev = revisions[-1]

        # Check if anything actually changed
        if last_rev.get("source_hash") == source_hash and last_rev.get("state_hash") == state_hash and last_rev.get("target_lang") == target_lang:
            return metadata, False  # No new version needed

        major, minor = map(int, metadata["current_version"].split('.'))

        if last_rev.get("source_hash") != source_hash or last_rev.get("target_lang") != target_lang:
            new_version = f"{major + 1}.0"
            change_summary = "Major update: Source code or target language changed."
        else:
            new_version = f"{major}.{minor + 1}"
            change_summary = "Minor update: Analysis, documentation, or recommendations revised."

        metadata["current_version"] = new_version
        metadata["status"] = "Revised"

    timestamp = datetime.now().isoformat()
    new_rev = {
        "version": metadata["current_version"],
        "timestamp": timestamp,
        "change_summary": change_summary,
        "review_status": metadata["status"],
        "generated_by": generated_by,
        "reviewed_by": "N/A",  # Removed reviewer logic
        "source_hash": source_hash,
        "target_lang": target_lang,
        "state_hash": state_hash
    }
    metadata["revisions"].append(new_rev)

    # Persist metadata
    filepath = os.path.join(METADATA_DIR, f"{doc_id}.json")
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)

    return metadata, True

def get_metadata(doc_id: str):
    filepath = os.path.join(METADATA_DIR, f"{doc_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None
