"""
Cloudinary template tags for optimized image rendering
"""

from django import template
from core.cloudinary_utils import CloudinaryHelper

register = template.Library()


@register.simple_tag
def cloudinary_url(
    public_id, width=None, height=None, crop="fill", quality="auto:good"
):
    """
    Get optimized Cloudinary URL
    Usage: {% cloudinary_url image.public_id width=800 height=400 %}
    """
    return CloudinaryHelper.get_optimized_url(public_id, width, height, crop, quality)


@register.simple_tag
def cloudinary_thumbnail(public_id, size=150):
    """
    Get thumbnail URL
    Usage: {% cloudinary_thumbnail image.public_id 100 %}
    """
    return CloudinaryHelper.get_thumbnail_url(public_id, size)


@register.simple_tag
def event_card_image(public_id):
    """
    Get event card optimized image
    Usage: {% event_card_image event.asset.public_id %}
    """
    return CloudinaryHelper.get_event_card_url(public_id)


@register.simple_tag
def event_hero_image(public_id):
    """
    Get event hero optimized image
    Usage: {% event_hero_image event.asset.public_id %}
    """
    return CloudinaryHelper.get_event_hero_url(public_id)


@register.simple_tag
def profile_avatar(public_id, size=100):
    """
    Get profile avatar optimized image
    Usage: {% profile_avatar user.profile_img.public_id 150 %}
    """
    return CloudinaryHelper.get_profile_avatar_url(public_id, size)


@register.filter
def has_cloudinary_image(field):
    """
    Check if field has a Cloudinary image
    Usage: {% if event.asset|has_cloudinary_image %}
    """
    return field and hasattr(field, "public_id") and field.public_id


@register.simple_tag
def default_event_image():
    """
    Get default event image URL
    Usage: {% default_event_image %}
    """
    return "/static/images/default_event.jpg"


@register.simple_tag
def default_profile_image():
    """
    Get default profile image URL
    Usage: {% default_profile_image %}
    """
    return "/static/images/default_profile.png"
