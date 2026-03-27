import uuid
import os
from django.db import models


def _upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"campus_{instance.campus_id}/{instance.entity_type}/{instance.asset_type}/{instance.id}{ext}"


class MediaAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campus_id = models.IntegerField(db_index=True)
    entity_type = models.CharField(max_length=64)   # e.g. 'applicant', 'student'
    asset_type = models.CharField(max_length=64)    # e.g. 'profile_photo', 'document'
    entity_id = models.CharField(max_length=64)     # UUID or int as string
    file = models.FileField(upload_to=_upload_to)
    mime_type = models.CharField(max_length=64)
    file_size = models.PositiveIntegerField(help_text='Size in bytes')
    uploaded_by_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'media_assets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.entity_type}/{self.asset_type} — {self.entity_id}"
