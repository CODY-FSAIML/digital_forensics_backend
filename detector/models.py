from django.db import models

class ForensicScan(models.Model):
    MEDIA_CHOICES = [
        ('VIDEO', 'Video'), 
        ('IMAGE', 'Image'), 
        ('AUDIO', 'Audio')
    ]
    
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES)
    file_name = models.CharField(max_length=255)
    is_fake = models.BooleanField(default=False)
    confidence = models.FloatField()
    reasons = models.JSONField(default=list) # Saves the glowing box text!
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.media_type}] {self.file_name} - {'FAKE' if self.is_fake else 'REAL'}"