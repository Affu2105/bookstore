from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    # Local storage field (used when S3 is disabled)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    
    # S3 storage fields
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    s3_key = models.CharField(max_length=255, null=True, blank=True)  # For deletion purposes

    def __str__(self):
        return self.title
        
    @property
    def get_image_url(self):
        """Returns the appropriate image URL based on storage type"""
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        return None