from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from PIL import Image
import uuid
import os
from io import BytesIO
from django.core.files.base import ContentFile


class Dream(models.Model):
    """Core model for storing dreams."""
    
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('specific_users', 'Specific Users'),
        ('groups', 'Groups'),
        ('community', 'Community'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dreams'
    )
    
    # Content
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(help_text="Dream description")
    voice_recording = models.FileField(
        upload_to='dream_recordings/%Y/%m/',
        null=True,
        blank=True,
        help_text="Voice recording of the dream"
    )
    transcription = models.TextField(
        blank=True,
        help_text="AI transcription of voice recording"
    )
    
    # Privacy settings
    privacy_level = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='private'
    )
    shared_with_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_dreams',
        blank=True
    )
    shared_with_groups = models.ManyToManyField(
        'sharing.DreamGroup',
        related_name='shared_dreams',
        blank=True
    )
    
    # Metadata
    dream_date = models.DateField(
        default=timezone.now,
        help_text="When the dream occurred"
    )
    mood = models.CharField(
        max_length=50,
        blank=True,
        help_text="Emotional tone of the dream"
    )
    lucidity_level = models.IntegerField(
        default=0,
        help_text="Lucidity level (0-10)"
    )
    
    # AI Analysis
    themes = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-identified themes"
    )
    symbols = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-identified symbols"
    )
    entities = models.JSONField(
        default=list,
        blank=True,
        help_text="People, places, objects in the dream"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dreams'
        ordering = ['-dream_date', '-created_at']
        indexes = [
            models.Index(fields=['-dream_date']),
            models.Index(fields=['user', '-dream_date']),
            models.Index(fields=['privacy_level']),
        ]
    
    def __str__(self):
        return f"{self.title or 'Untitled Dream'} - {self.dream_date}"
    
    def get_absolute_url(self):
        return reverse('dreams:detail', kwargs={'pk': self.pk})
    
    @property
    def is_private(self):
        return self.privacy_level == 'private'
    
    @property
    def is_shared(self):
        return self.privacy_level != 'private'
    
    def is_public_dream(self):
        """Check if dream should be indexed in Algolia (only community dreams)."""
        return self.privacy_level == 'community'


class DreamTag(models.Model):
    """User-defined tags for dreams."""
    
    name = models.CharField(max_length=50, unique=True)
    dreams = models.ManyToManyField(Dream, related_name='tags')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dream_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


def dream_image_upload_path(instance, filename):
    """Generate upload path for dream images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"dream_images/{instance.dream.user.id}/{instance.dream.id}/{filename}"


class DreamImage(models.Model):
    """Images associated with dreams."""
    
    dream = models.ForeignKey(
        Dream,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=dream_image_upload_path,
        null=True,
        blank=True,
        help_text="Upload an image from your computer"
    )
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Or provide a URL to an image"
    )
    thumbnail = models.ImageField(
        upload_to=dream_image_upload_path,
        null=True,
        blank=True,
        editable=False
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional caption for the image"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Order of display (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dream_images'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['dream', 'order']),
        ]
    
    def __str__(self):
        return f"Image for {self.dream.title or 'Untitled Dream'}"
    
    def clean(self):
        """Validate that either image or image_url is provided, but not both."""
        if not self.image and not self.image_url:
            raise ValidationError("Either upload an image or provide an image URL.")
        if self.image and self.image_url:
            raise ValidationError("Please provide either an image upload or URL, not both.")
        
        # Check max images per dream
        if self.dream_id:
            existing_count = DreamImage.objects.filter(dream=self.dream).exclude(pk=self.pk).count()
            if existing_count >= 3:
                raise ValidationError("A dream can have a maximum of 3 images.")
    
    def save(self, *args, **kwargs):
        """Process and optimize image before saving."""
        if self.image:
            # Open the image
            img = Image.open(self.image)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Update the image field
            self.image = ContentFile(output.read(), name=self.image.name.replace('.png', '.jpg'))
            
            # Create thumbnail (300x300)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            thumb_output = BytesIO()
            img.save(thumb_output, format='JPEG', quality=85, optimize=True)
            thumb_output.seek(0)
            
            # Save thumbnail
            thumb_name = f"thumb_{self.image.name}"
            self.thumbnail = ContentFile(thumb_output.read(), name=thumb_name)
        
        super().save(*args, **kwargs)
    
    @property
    def display_url(self):
        """Return the URL for displaying the image."""
        if self.image:
            return self.image.url
        return self.image_url
    
    @property
    def thumbnail_url(self):
        """Return the thumbnail URL or fallback to main image."""
        if self.thumbnail:
            return self.thumbnail.url
        return self.display_url
