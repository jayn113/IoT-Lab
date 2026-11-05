import json
from datetime import datetime
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("/home/jayn/IOT-Lab")
DATA_FILE = BASE / "data.json"
OUTPUT_FILE = BASE / "aws_upload_preview.json"

DEVICE_ID = "pi1"

def prepare_records():
    with DATA_FILE.open("r") as f:
        data = json.load(f)

    messages = []

    for table_name in ("sensor_readings", "camera_records"):
        records = data.get(table_name, {})

        for record_id, record in records.items():
            if not isinstance(record, dict):
                continue

            payload = dict(record)

            payload["device_id"] = f"{DEVICE_ID}:{table_name}"
            payload["timestamp"] = (
                str(record.get("timestamp"))
                if record.get("timestamp")
                else datetime.now(timezone.utc).isoformat()
            ) + f"#{record_id}"

            payload["record_type"] = table_name
            payload["tinydb_id"] = str(record_id)

            messages.append(payload)

    return messages


def upload_to_cloud(dry_run=True):
    messages = prepare_records()

    if dry_run:
        OUTPUT_FILE.write_text(
            json.dumps(messages, indent=2)
        )

        return {
            "STATUS": "dry_run",
            "RECORDS_PREPARED": len(messages),
            "OUTPUT_FILE": str(OUTPUT_FILE),
            "UPLOAD_TIMESTAMP": datetime.now().isoformat()
        }

    raise RuntimeError(
        "Real AWS uploads are disabled until the account is reactivated."
    )


if __name__ == "__main__":
    print(upload_to_cloud(dry_run=True))
