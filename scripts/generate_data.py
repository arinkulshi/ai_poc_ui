"""Generate dummy email data for testing."""
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()

# Configuration
NUM_EMAILS = 30000
TOPICS = [
    "Kosovo Peacekeeping Strategy",
    "NAFTA Trade Agreement impact",
    "Health Care Task Force",
    "Balkans security briefing",
    "Drug Policy enforcement",
    "Education reform initiative",
    "Technology partnership 2000",
    "White House visitor protocols"
]

AGENCIES = ["NSC", "WHO", "OSTP", "OMB"]

# Output to project root
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "dummy_emails.jsonl"


def generate_email():
    topic = random.choice(TOPICS)

    start_date = datetime(1993, 1, 20)
    end_date = datetime(2001, 1, 20)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    date_obj = start_date + timedelta(days=random_days)

    body_text = (
        f"Regarding the {topic}: \n\n"
        + fake.paragraph(nb_sentences=5)
        + "\n\n"
        + fake.paragraph(nb_sentences=3)
    )

    return {
        "id": str(uuid.uuid4()),
        "structData": {
            "email_id": fake.random_int(min=10000, max=99999),
            "subject": f"Memo: {topic} - {fake.catch_phrase()}",
            "abstract": (
                f"This record discusses the {topic} strategy. "
                f"Key points include {fake.bs()} and the impact on {fake.job()}. "
                f"Authored by {fake.last_name()} for review by the {random.choice(AGENCIES)}."
            ),
            "date": date_obj.isoformat(),
            "author": f"{fake.last_name()}@eop.gov",
            "to": ", ".join([f"{fake.last_name()}@eop.gov" for _ in range(random.randint(1, 5))]),
            "text_content": body_text,
            "agency": random.choice(AGENCIES),
            "url": f"https://fake-archive.nara.gov/emails/{fake.uuid4()}",
            "attachments_count": random.randint(0, 3)
        }
    }


if __name__ == "__main__":
    print(f"Generating {NUM_EMAILS} dummy emails...")
    with open(OUTPUT_PATH, "w") as f:
        for _ in range(NUM_EMAILS):
            email = generate_email()
            f.write(json.dumps(email) + "\n")
    print(f"Done! File '{OUTPUT_PATH}' created.")
