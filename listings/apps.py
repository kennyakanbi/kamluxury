from django.apps import AppConfig

class ListingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'listings'

    def ready(self):
        from .startup import create_admin_user
        create_admin_user()
