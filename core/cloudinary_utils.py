"""
Cloudinary utilities for image optimization and transformations
"""

import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage


class CloudinaryHelper:
    """Helper class for Cloudinary operations"""

    @staticmethod
    def get_optimized_url(
        public_id, width=None, height=None, crop="fill", quality="auto:good"
    ):
        """
        Get optimized image URL with transformations
        """
        if not public_id:
            return None

        transformations = {
            "quality": quality,
            "fetch_format": "auto",
        }

        if width:
            transformations["width"] = width
        if height:
            transformations["height"] = height
        if crop:
            transformations["crop"] = crop

        return CloudinaryImage(public_id).build_url(**transformations)

    @staticmethod
    def get_thumbnail_url(public_id, size=150):
        """Get thumbnail URL for images"""
        return CloudinaryHelper.get_optimized_url(
            public_id, width=size, height=size, crop="thumb", quality="auto:low"
        )

    @staticmethod
    def get_event_card_url(public_id):
        """Get URL optimized for event cards"""
        return CloudinaryHelper.get_optimized_url(
            public_id, width=400, height=250, crop="fill"
        )

    @staticmethod
    def get_event_hero_url(public_id):
        """Get URL optimized for event hero sections"""
        return CloudinaryHelper.get_optimized_url(
            public_id, width=800, height=400, crop="fill"
        )

    @staticmethod
    def get_profile_avatar_url(public_id, size=100):
        """Get URL optimized for profile avatars"""
        return CloudinaryHelper.get_optimized_url(
            public_id, width=size, height=size, crop="fill", quality="auto:good"
        )

    @staticmethod
    def upload_image(image_file, folder, public_id=None, transformations=None):
        """
        Upload image to Cloudinary with optimizations
        """
        upload_options = {
            "folder": folder,
            "quality": "auto:good",
            "fetch_format": "auto",
        }

        if public_id:
            upload_options["public_id"] = public_id

        if transformations:
            upload_options["transformation"] = transformations

        try:
            result = cloudinary.uploader.upload(image_file, **upload_options)
            return result
        except Exception as e:
            print(f"Error uploading to Cloudinary: {str(e)}")
            return None

    @staticmethod
    def delete_image(public_id):
        """Delete image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            print(f"Error deleting from Cloudinary: {str(e)}")
            return False


# Template tags for easy use in templates
def cloudinary_url(public_id, **kwargs):
    """Template tag for getting Cloudinary URLs"""
    return CloudinaryHelper.get_optimized_url(public_id, **kwargs)


def cloudinary_thumbnail(public_id, size=150):
    """Template tag for thumbnails"""
    return CloudinaryHelper.get_thumbnail_url(public_id, size)
