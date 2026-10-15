import json
import time
from awscrt import mqtt
from awsiot import mqtt_connection_builder


# ----------------------------
# AWS SETTINGS
# ----------------------------

ENDPOINT = "a3c8u82riksvor-ats.iot.us-east-1.amazonaws.com"

CLIENT_ID = "ee4201-raspberry-pi"

TOPIC = "ee4201/sensors"

CERTIFICATE = "certs/e5eee297c12f6abdf1622680a4de2be4cb250ad7a370938b97be2686fe087495-certificate.pem.crt"

PRIVATE_KEY = "certs/e5eee297c12f6abdf1622680a4de2be4cb250ad7a370938b97be2686fe087495-private.pem.key"

ROOT_CA = "certs/AmazonRootCA1.pem"


# ----------------------------
# CONNECT TO AWS
# ----------------------------

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERTIFICATE,
    pri_key_filepath=PRIVATE_KEY,
    ca_filepath=ROOT_CA,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30
)

print("Connecting to AWS IoT...")

mqtt_connection.connect().result()

print("Connected!")


# ----------------------------
# READ TINYDB JSON
# ----------------------------

with open("sensor_data.json", "r") as file:
    tinydb_data = json.load(file)


records = tinydb_data["_default"]


# ----------------------------
# UPLOAD EACH RECORD
# ----------------------------

for record_id, record in records.items():

    # DynamoDB requires device_id
    record["device_id"] = "pi1"

    payload = json.dumps(record)

    print("Uploading record", record_id)
    print(payload)

    mqtt_connection.publish(
        topic=TOPIC,
        payload=payload,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )

    # Small delay between messages
    time.sleep(0.5)


print("All TinyDB records uploaded!")

mqtt_connection.disconnect().result()
