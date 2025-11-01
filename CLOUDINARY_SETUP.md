# Cloudinary Integration Guide

## Overview

This project now uses Cloudinary for advanced image management, optimization, and delivery. Cloudinary provides automatic image optimization, transformations, and a global CDN for better performance.

## Features Implemented

### 🌟 Key Benefits

- **Automatic Optimization**: Images are automatically optimized for web delivery
- **Responsive Images**: Different sizes generated automatically for different devices
- **CDN Delivery**: Fast global content delivery network
- **Format Selection**: Automatic format selection (WebP, AVIF, etc.)
- **Quality Optimization**: Smart quality optimization based on content
- **Face Detection**: Profile images automatically cropped to focus on faces

### 📸 Image Types Handled

1. **Event Images**: Banner images for events with 800x400 optimization
2. **Profile Images**: User profile pictures with 400x400 face-focused cropping
3. **Thumbnails**: Automatically generated for cards and lists

## Setup Instructions

### 1. Cloudinary Account Setup

1. Sign up at [Cloudinary](https://cloudinary.com/)
2. Get your credentials from the dashboard:
   - Cloud Name
   - API Key
   - API Secret

### 2. Environment Configuration

Add these variables to your `.env` file:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. Install Dependencies

```bash
pip install cloudinary django-cloudinary-storage
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Migrate Existing Images (Optional)

To migrate existing local images to Cloudinary:

```bash
# Migrate all images
python manage.py migrate_to_cloudinary

# Migrate only event images
python manage.py migrate_to_cloudinary --events-only

# Migrate only profile images
python manage.py migrate_to_cloudinary --users-only
```

## Usage in Templates

### Load the Template Tags

```django
{% load cloudinary_tags %}
```

### Basic Image Display

```django
<!-- Event card image (400x250, optimized) -->
<img src="{% event_card_image event.asset.public_id %}" alt="{{ event.name }}">

<!-- Event hero image (800x400, optimized) -->
<img src="{% event_hero_image event.asset.public_id %}" alt="{{ event.name }}">

<!-- Profile avatar (100x100, face-focused) -->
<img src="{% profile_avatar user.profile_img.public_id 100 %}" alt="{{ user.username }}">

<!-- Custom transformations -->
<img src="{% cloudinary_url image.public_id width=600 height=300 crop='fill' %}" alt="Custom">
```

### Responsive Images

```django
<!-- Different sizes for different screen sizes -->
<picture>
  <source media="(max-width: 640px)"
          srcset="{% cloudinary_url event.asset.public_id width=400 height=200 %}">
  <source media="(max-width: 1024px)"
          srcset="{% cloudinary_url event.asset.public_id width=600 height=300 %}">
  <img src="{% cloudinary_url event.asset.public_id width=800 height=400 %}"
       alt="{{ event.name }}">
</picture>
```

### Default Images

```django
<!-- With fallback to default -->
{% if event.asset|has_cloudinary_image %}
  <img src="{% event_card_image event.asset.public_id %}" alt="{{ event.name }}">
{% else %}
  <img src="{% default_event_image %}" alt="Default Event">
{% endif %}
```

## Models

### Event Model

```python
class Event(models.Model):
    # ... other fields
    asset = CloudinaryField(
        'image',
        blank=True,
        null=True,
        folder="event_assets",
        transformation={
            'quality': 'auto:good',
            'fetch_format': 'auto',
            'width': 800,
            'height': 400,
            'crop': 'fill',
        }
    )
```

### User Model

```python
class CustomUser(AbstractUser):
    # ... other fields
    profile_img = CloudinaryField(
        'image',
        blank=True,
        folder="profile_images",
        transformation={
            'quality': 'auto:good',
            'fetch_format': 'auto',
            'width': 400,
            'height': 400,
            'crop': 'fill',
            'gravity': 'face',
        }
    )
```

## Available Template Tags

| Tag                    | Purpose                     | Usage                                             |
| ---------------------- | --------------------------- | ------------------------------------------------- | ------------------------ |
| `cloudinary_url`       | Custom transformations      | `{% cloudinary_url image.public_id width=800 %}`  |
| `cloudinary_thumbnail` | Generate thumbnails         | `{% cloudinary_thumbnail image.public_id 150 %}`  |
| `event_card_image`     | Event card optimization     | `{% event_card_image event.asset.public_id %}`    |
| `event_hero_image`     | Event hero optimization     | `{% event_hero_image event.asset.public_id %}`    |
| `profile_avatar`       | Profile avatar optimization | `{% profile_avatar user.profile_img.public_id %}` |
| `has_cloudinary_image` | Check if image exists       | `{% if field                                      | has_cloudinary_image %}` |

## Performance Benefits

### Before Cloudinary

- Large image files served from local storage
- No automatic optimization
- Single format (JPEG/PNG)
- No CDN delivery
- Manual image resizing required

### After Cloudinary

- ✅ Automatic image compression (30-80% size reduction)
- ✅ Format optimization (WebP, AVIF when supported)
- ✅ Responsive image generation
- ✅ Global CDN delivery
- ✅ Lazy loading support
- ✅ Face detection for profile images

## Folder Structure in Cloudinary

```
your-cloud-name/
├── event_assets/          # Event banner images
│   ├── event_1_conference
│   └── event_2_workshop
└── profile_images/        # User profile pictures
    ├── user_1_john_doe
    └── user_2_jane_smith
```

## Troubleshooting

### Common Issues

1. **Images not loading**: Check Cloudinary credentials in `.env`
2. **Migration errors**: Ensure Cloudinary is properly configured before running migrations
3. **Template errors**: Make sure to load `{% load cloudinary_tags %}` in templates

### Rollback to Local Storage

If needed, you can rollback by:

1. Commenting out Cloudinary apps in `INSTALLED_APPS`
2. Reverting model fields to `ImageField`
3. Running new migrations

## Cost Optimization

- Free tier includes 25 GB storage and 25 GB bandwidth
- Automatic optimization reduces bandwidth usage
- Smart cropping reduces storage needs
- Efficient caching reduces API calls
