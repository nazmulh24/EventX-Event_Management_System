"""
Management command to migrate existing local images to Cloudinary
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from events.models import Event
from users.models import CustomUser
import cloudinary.uploader


class Command(BaseCommand):
    help = "Migrate existing local images to Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--events-only",
            action="store_true",
            help="Migrate only event images",
        )
        parser.add_argument(
            "--users-only",
            action="store_true",
            help="Migrate only user profile images",
        )

    def handle(self, *args, **options):
        if options["events_only"]:
            self.migrate_event_images()
        elif options["users_only"]:
            self.migrate_user_images()
        else:
            self.migrate_event_images()
            self.migrate_user_images()

    def migrate_event_images(self):
        self.stdout.write(self.style.SUCCESS("Starting event image migration..."))

        events = Event.objects.filter(asset__isnull=False)

        for event in events:
            try:
                # Skip if already using Cloudinary
                if hasattr(event.asset, "public_id"):
                    self.stdout.write(f"Event {event.name} already using Cloudinary")
                    continue

                # Get the full path to the image
                image_path = os.path.join(settings.MEDIA_ROOT, str(event.asset))

                if os.path.exists(image_path):
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        image_path,
                        folder="event_assets",
                        public_id=f"event_{event.id}_{event.name[:20]}",
                        transformation={
                            "quality": "auto:good",
                            "fetch_format": "auto",
                            "width": 800,
                            "height": 400,
                            "crop": "fill",
                        },
                    )

                    # Update the event with Cloudinary URL
                    event.asset = result["public_id"]
                    event.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Migrated image for event: {event.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Image not found for event: {event.name}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Error migrating image for event {event.name}: {str(e)}"
                    )
                )

    def migrate_user_images(self):
        self.stdout.write(
            self.style.SUCCESS("Starting user profile image migration...")
        )

        users = CustomUser.objects.filter(profile_img__isnull=False)

        for user in users:
            try:
                # Skip if already using Cloudinary
                if hasattr(user.profile_img, "public_id"):
                    self.stdout.write(f"User {user.username} already using Cloudinary")
                    continue

                # Get the full path to the image
                image_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_img))

                if os.path.exists(image_path):
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        image_path,
                        folder="profile_images",
                        public_id=f"user_{user.id}_{user.username}",
                        transformation={
                            "quality": "auto:good",
                            "fetch_format": "auto",
                            "width": 400,
                            "height": 400,
                            "crop": "fill",
                            "gravity": "face",
                        },
                    )

                    # Update the user with Cloudinary URL
                    user.profile_img = result["public_id"]
                    user.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Migrated profile image for user: {user.username}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Profile image not found for user: {user.username}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Error migrating profile image for user {user.username}: {str(e)}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("🎉 Migration completed!"))
