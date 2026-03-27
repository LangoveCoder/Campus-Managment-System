"""
MediaService — handles upload, retrieval, and deletion of MediaAsset objects.
Constitutional rule: no ORM beyond this service layer.
"""

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class MediaValidationError(Exception):
    pass


class MediaService:

    @staticmethod
    def upload(campus_id, entity_type, asset_type, entity_id, file_obj, uploaded_by_id=None):
        """
        Validate and store a file. Returns the saved MediaAsset instance.
        Raises MediaValidationError on invalid file.
        """
        from modules.media.models import MediaAsset

        # --- Validation ---
        mime = getattr(file_obj, 'content_type', None)
        if mime not in ALLOWED_MIME_TYPES:
            raise MediaValidationError(
                f"File type '{mime}' is not allowed. Accepted: JPEG, PNG, PDF."
            )

        size = file_obj.size
        if size > MAX_FILE_SIZE:
            raise MediaValidationError(
                f"File too large ({size // 1024}KB). Maximum allowed is 5MB."
            )

        # --- Persist ---
        asset = MediaAsset(
            campus_id=campus_id,
            entity_type=entity_type,
            asset_type=asset_type,
            entity_id=str(entity_id),
            mime_type=mime,
            file_size=size,
            uploaded_by_id=str(uploaded_by_id) if uploaded_by_id else None,
        )
        asset.file = file_obj
        asset.save()
        return asset

    @staticmethod
    def get_for_entity(campus_id, entity_type, entity_id):
        """Return all assets for a given entity, campus-scoped."""
        from modules.media.models import MediaAsset
        return list(
            MediaAsset.objects.filter(
                campus_id=campus_id,
                entity_type=entity_type,
                entity_id=str(entity_id),
            )
        )

    @staticmethod
    def get_profile_photo(campus_id, entity_type, entity_id):
        """Return the most recent profile_photo asset or None."""
        from modules.media.models import MediaAsset
        return (
            MediaAsset.objects
            .filter(
                campus_id=campus_id,
                entity_type=entity_type,
                entity_id=str(entity_id),
                asset_type='profile_photo',
            )
            .order_by('-created_at')
            .first()
        )

    @staticmethod
    def delete(asset_id, campus_id):
        """Delete an asset by UUID, enforcing campus scope. Returns True if deleted."""
        from modules.media.models import MediaAsset
        try:
            asset = MediaAsset.objects.get(id=asset_id, campus_id=campus_id)
            asset.file.delete(save=False)
            asset.delete()
            return True
        except MediaAsset.DoesNotExist:
            return False
