"""
producer.py — Experiment 5: Real-Time Streaming Data Processing
using Databricks & Azure Event Hub.

Simulates real-time student activity events and sends 50 events
to the Event Hub entity calab-eventhub-141.

Prerequisites:
    pip install azure-eventhub

    Replace EVENT_HUB_CONNECTION_STRING with the Primary Connection
    String of the DatabricksPolicy SAS policy. Do NOT commit a real
    connection string to GitHub.
"""

import json
import random
import time
from datetime import datetime, timezone

from azure.eventhub import EventHubProducerClient, EventData

# ---------------------------------------------------------------------------
# Configuration — replace the placeholder before running
# ---------------------------------------------------------------------------
EVENT_HUB_CONNECTION_STRING = "<DatabricksPolicy primary connection string>"
EVENT_HUB_NAME = "calab-eventhub-141"
TOTAL_EVENTS = 50
BATCH_SIZE = 10

STUDENTS = [
    "Abhi",
    "Ananya",
    "Rahul",
    "Priya",
    "Vikram",
    "Sneha",
    "Arjun",
    "Meera",
]

EVENT_TYPES = [
    "login",
    "video_view",
    "quiz_submit",
    "assignment_submit",
    "discussion_post",
]


def make_event() -> dict:
    """Build one simulated student activity event."""
    event_type = random.choice(EVENT_TYPES)
    # A score only makes sense for a quiz submission; other events
    # carry no score (None -> null in JSON, ignored by avg() later).
    score = random.randint(55, 100) if event_type == "quiz_submit" else None
    return {
        "student_name": random.choice(STUDENTS),
        "event_type": event_type,
        "score": score,
        "event_time": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STRING,
        eventhub_name=EVENT_HUB_NAME,
    )
    try:
        sent = 0
        batch = producer.create_batch()
        for _ in range(TOTAL_EVENTS):
            event = make_event()
            try:
                batch.add(EventData(json.dumps(event)))
            except ValueError:
                # Batch is full: flush it and start a new one.
                producer.send_batch(batch)
                sent += len(batch)
                batch = producer.create_batch()
                batch.add(EventData(json.dumps(event)))
            print(f"Prepared: {event}")
            if len(batch) >= BATCH_SIZE:
                producer.send_batch(batch)
                sent += len(batch)
                print(f"Sent batch — {sent}/{TOTAL_EVENTS} events sent so far")
                batch = producer.create_batch()
                time.sleep(0.5)

        if len(batch) > 0:
            producer.send_batch(batch)
            sent += len(batch)

        print(f"Done — {sent} student activity events sent to {EVENT_HUB_NAME}")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
