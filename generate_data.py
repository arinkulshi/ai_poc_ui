import json
import random
import uuid
from datetime import datetime, timedelta
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

def generate_email():
    # Pick a topic to ensure semantic consistency
    topic = random.choice(TOPICS)
    
    # Generate realistic dates (Clinton era: 1993-2001)
    start_date = datetime(1993, 1, 20)
    end_date = datetime(2001, 1, 20)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    date_obj = start_date + timedelta(days=random_days)
    
    # Construct the "Clean" body text
    # We inject the topic into the body to ensure vector similarity works
    body_text = f"Regarding the {topic}: \n\n" + fake.paragraph(nb_sentences=5) + "\n\n" + fake.paragraph(nb_sentences=3)

    # Construct the Document object structure expected by Agent Builder
    # Root fields must match the google.cloud.discoveryengine.v1.Document proto
    return {
        "id": str(uuid.uuid4()),
        "structData": {
            "email_id": fake.random_int(min=10000, max=99999),
            "subject": f"Memo: {topic} - {fake.catch_phrase()}",
            "abstract": f"This record discusses the {topic} strategy. Key points include {fake.bs()} and the impact on {fake.job()}. Authored by {fake.last_name()} for review by the {random.choice(AGENCIES)}.",
            "date": date_obj.isoformat(),
            "author": f"{fake.last_name()}@eop.gov",
            "to": ", ".join([f"{fake.last_name()}@eop.gov" for _ in range(random.randint(1, 5))]),
            "text_content": body_text,
            "agency": random.choice(AGENCIES),
            "url": f"https://fake-archive.nara.gov/emails/{fake.uuid4()}",
            "attachments_count": random.randint(0, 3)
        }
    }

# Generate and Save
print(f"Generating {NUM_EMAILS} dummy emails...")
with open("dummy_emails.jsonl", "w") as f:
    for _ in range(NUM_EMAILS):
        email = generate_email()
        f.write(json.dumps(email) + "\n")

print("Done! File 'dummy_emails.jsonl' created.")
