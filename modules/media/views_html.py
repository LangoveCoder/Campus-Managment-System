from django.shortcuts import render, redirect
from django.http import JsonResponse
from modules.media.services import MediaService, MediaValidationError
from modules.media.auth import AuthorizationFacade


def _get_campus_id(request):
    campus_id = request.session.get('current_campus_id')
    return int(campus_id) if campus_id else None


def _get_person_id(request):
    person = getattr(request.user, 'person', None)
    return str(person.id) if person else None


def upload_view(request):
    """Authenticated upload view — requires media.upload_media permission."""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    campus_id = _get_campus_id(request)
    if not campus_id:
        return redirect('/select-campus/')

    person_id = _get_person_id(request)
    try:
        AuthorizationFacade.require(person_id, campus_id, 'media.upload_media')
    except Exception:
        return render(request, 'media/upload.html', {
            'error': 'You do not have permission to upload media.',
            'active_section': 'media',
        }, status=403)

    error = None
    success = None

    if request.method == 'POST':
        entity_type = request.POST.get('entity_type', '').strip()
        asset_type = request.POST.get('asset_type', '').strip()
        entity_id = request.POST.get('entity_id', '').strip()
        file_obj = request.FILES.get('file')

        if not all([entity_type, asset_type, entity_id, file_obj]):
            error = 'All fields are required.'
        else:
            try:
                asset = MediaService.upload(
                    campus_id=campus_id,
                    entity_type=entity_type,
                    asset_type=asset_type,
                    entity_id=entity_id,
                    file_obj=file_obj,
                    uploaded_by_id=person_id,
                )
                success = f"File uploaded successfully. Asset ID: {asset.id}"
            except MediaValidationError as e:
                error = str(e)

    return render(request, 'media/upload.html', {
        'error': error,
        'success': success,
        'active_section': 'media',
    })


def applicant_upload_view(request):
    """
    Public (unauthenticated) upload for applicants.
    Restricted to entity_type='applicant', asset_type in [profile_photo, document].
    """
    ALLOWED_ENTITY_TYPES = {'applicant'}
    ALLOWED_ASSET_TYPES = {'profile_photo', 'document'}

    error = None
    success = None

    if request.method == 'POST':
        entity_type = request.POST.get('entity_type', '').strip()
        asset_type = request.POST.get('asset_type', '').strip()
        entity_id = request.POST.get('entity_id', '').strip()
        campus_id = request.POST.get('campus_id', '').strip()
        file_obj = request.FILES.get('file')

        if entity_type not in ALLOWED_ENTITY_TYPES:
            error = 'Invalid entity type for public upload.'
        elif asset_type not in ALLOWED_ASSET_TYPES:
            error = 'Invalid asset type for public upload.'
        elif not all([entity_id, campus_id, file_obj]):
            error = 'All fields are required.'
        else:
            try:
                asset = MediaService.upload(
                    campus_id=int(campus_id),
                    entity_type=entity_type,
                    asset_type=asset_type,
                    entity_id=entity_id,
                    file_obj=file_obj,
                    uploaded_by_id=None,
                )
                success = f"File uploaded successfully."
            except (MediaValidationError, ValueError) as e:
                error = str(e)

    return render(request, 'media/applicant_upload.html', {
        'error': error,
        'success': success,
    })
