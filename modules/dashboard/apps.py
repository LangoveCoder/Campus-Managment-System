from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.dashboard'
    verbose_name = 'Dashboard'

    # No permissions registered — the dashboard uses existing module permissions only.
    # No models — the dashboard owns no data.
