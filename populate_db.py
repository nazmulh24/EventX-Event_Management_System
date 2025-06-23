import os
import django
from faker import Faker
import random

from events.models import Category, Event, Participant

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management.settings")
django.setup()

# Sample Bangladeshi locations (area + zone + city)
LOCATIONS = [
    "Gulshan-2, Dhaka",
    "Dhanmondi-29, Dhaka",
    "Uttara Sector-11, Dhaka",
    "Banani, Dhaka",
    "Mohakhali DOHS, Dhaka",
    "Mirpur-10, Dhaka",
    "Shyamoli, Dhaka",
    "Bashundhara R/A, Dhaka",
    "Tejgaon, Dhaka",
    "Motijheel, Dhaka",
    "Farmgate, Dhaka",
    "Malibagh, Dhaka",
    "Jatrabari, Dhaka",
    "Mohammadpur, Dhaka",
    "Rampura, Dhaka",
]

# Category list with description
CATEGORIES = [
    ("Tech", "Technology and IT related events"),
    ("Edu", "Education fairs and seminars"),
    ("Biz", "Business and startup events"),
    ("Health", "Health camps and wellness sessions"),
    ("Art", "Photography and art exhibitions"),
    ("Books", "Book fairs and author meets"),
    ("Islam", "Islamic mahfil and religious discussions"),
    ("Culture", "Cultural programs and shows"),
    ("Youth", "Campus and youth events"),
    ("Social", "Community and charity drives"),
]


def populate_db():
    fake = Faker()

    # Clear existing data (optional)
    Category.objects.all().delete()
    Event.objects.all().delete()
    Participant.objects.all().delete()

    # Create Categories
    categories = []
    for name, desc in CATEGORIES:
        category = Category.objects.create(name=name, description=desc)
        categories.append(category)
    print(f"✅ Created {len(categories)} categories")

    # Create Events
    events = []
    for _ in range(20):
        event = Event.objects.create(
            name=fake.catch_phrase(),
            description=fake.paragraph(),
            date=fake.date_between(start_date="-4d", end_date="+60d"),
            time=fake.time(pattern="%H:%M"),
            location=random.choice(LOCATIONS),
            category=random.choice(categories),
        )
        events.append(event)
    print(f"✅ Created {len(events)} events")

    # Create Participants and assign to random events
    for _ in range(60):
        participant = Participant.objects.create(
            name=fake.name(),
            email=fake.unique.email(),
        )
        selected_events = random.sample(events, k=random.randint(1, 3))
        participant.events.set(selected_events)
    print("✅ Created 60 participants and linked to events")
    print("🎉 Dummy data populated successfully!")


if __name__ == "__main__":
    populate_db()

