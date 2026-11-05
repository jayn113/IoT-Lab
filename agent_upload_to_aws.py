import json
import hashlib
from datetime import datetime
from pathlib import Path
from datetime import datetime, timezone

from awscrt import mqtt
from awsiot import mqtt_connection_builder

BASE = Path("/home/jayn/IOT-Lab").resolve().parent

ENDPOINT = "a3c8u82riksvor-ats.iot.us-east-1.amazonaws.com"
TOPIC = "ee4201/sensors"
CLIENT_ID = "ee4201-aws-uploader"
DEVICE_ID = "pi1"

DATA_FILE = BASE / "data.json"
STATE_FILE = BASE / ".aws_upload_state.json"

CERT = "certs/e5eee297c12f6abdf1622680a4de2be4cb250ad7a370938b97be2686fe087495-certificate.pem.crt"
KEY = "certs/e5eee297c12f6abdf1622680a4de2be4cb250ad7a370938b97be2686fe087495-private.pem.key"
CA = "certs/AmazonRootCA1.pem"


def load_json(path, default):
    if not path.exists():
        return default
    with path.open("r") as f:
        return json.load(f)


def upload_databases():
    data = load_json(DATA_FILE, {})
    synced = set(load_json(STATE_FILE, []))

    connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=str(CERT),
        pri_key_filepath=str(KEY),
        ca_filepath=str(CA),
        client_id=CLIENT_ID,
        clean_session=True,
        keep_alive_secs=30,
    )

    uploaded = 0
    skipped = 0

    try:
        connection.connect().result(timeout=30)
        print("Connected to AWS IoT Core")

        for table_name in ("sensor_readings", "camera_records"):
            records = data.get(table_name, {})

            for record_id, record in records.items():
                if not isinstance(record, dict):
                    continue

                # Distinguish camera and sensor records.
                device_id = f"{DEVICE_ID}:{table_name}"

                timestamp = (
                    record.get("timestamp")
                    or record.get("TIMESTAMP")
                    or datetime.now(timezone.utc).isoformat()
                )

                # Unique, repeatable identifier for sync tracking.
                sync_id = f"{table_name}:{record_id}"
                if sync_id in synced:
                    skipped += 1
                    continue

                # Preserve the original sensor/camera attributes.
                payload = dict(record)
                payload["device_id"] = device_id
                payload["timestamp"] = str(timestamp)
                payload["record_type"] = table_name
                payload["tinydb_id"] = str(record_id)

                # Prevent timestamp-key collisions for records
                # from the same table and device.
                payload["timestamp"] += f"#{record_id}"

                message = json.dumps(payload)

                future, _ = connection.publish(
                    topic=TOPIC,
                    payload=message,
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                )

                # Wait for AWS IoT to acknowledge the publish.
                future.result(timeout=30)

                synced.add(sync_id)
                STATE_FILE.write_text(
                    json.dumps(sorted(synced), indent=2)
                )

                uploaded += 1
                print(f"Published {sync_id}")

        return {
            "STATUS": "mqtt_published",
            "UPLOADED": uploaded,
            "SKIPPED": skipped,
            "TIMESTAMP": datetime.now().isoformat()
        }

    finally:
        connection.disconnect().result(timeout=30)


if __name__ == "__main__":
    print(upload_databases())
